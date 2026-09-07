#pragma once

// Two-value row hints for large user-input tensors (causal KQ masks, sparse-attention block
// biases). A row that is one value for a prefix and another value for the rest is described by
// its prefix length; the scheduler can then expand it on the device instead of uploading it.
// Every row is proven bit for bit with memcmp before a hint is published, so any other content
// keeps the ordinary host copy.

#include "ggml.h"
#include "ggml-backend.h"
#include "ggml-research.h"

#include <cstdlib>
#include <cstring>
#include <vector>

static inline bool llama_input_mask_hint_enabled() {
    // runtime research selector (see ggml-research.h); cached per generation
    static ggml_research_cached_int selector;
    return selector.get("GGML_SCHED_DEVICE_MASK", 0) != 0;
}

// T is the element type (ggml_fp16_t or float, compared as raw bits). Returns true when a hint was published.
template <typename T>
static inline bool llama_publish_input_mask_hint(ggml_tensor * dst, int64_t n_rows, int64_t n_cols) {
    if (!llama_input_mask_hint_enabled() || dst == nullptr || dst->data == nullptr || n_rows <= 0 || n_cols <= 0 || n_cols % 2 != 0 ||
            (int64_t) ggml_type_size(dst->type) != (int64_t) sizeof(T)) {
        ggml_backend_tensor_clear_input_mask_hint(dst);
        return false;
    }
    const T * data = (const T *) dst->data;
    // the two row values come from the first row's ends; every row must use the same pair
    T a, b;
    memcpy(&a, data, sizeof(T));
    memcpy(&b, data + (n_cols - 1), sizeof(T));
    static thread_local std::vector<T> ref_a, ref_b;
    static thread_local T ref_a_val, ref_b_val;
    if ((int64_t) ref_a.size() < n_cols || memcmp(&ref_a_val, &a, sizeof(T)) != 0 || memcmp(&ref_b_val, &b, sizeof(T)) != 0) {
        ref_a.assign(n_cols, a);
        ref_b.assign(n_cols, b);
        ref_a_val = a;
        ref_b_val = b;
    }
    std::vector<int32_t> prefix((size_t) n_rows);
    for (int64_t i = 0; i < n_rows; ++i) {
        const T * row = data + i*n_cols;
        // binary search the first non-`a` element assuming a monotone row, then prove it
        int64_t lo = 0, hi = n_cols;
        while (lo < hi) {
            const int64_t mid = (lo + hi)/2;
            if (memcmp(row + mid, &a, sizeof(T)) == 0) { lo = mid + 1; } else { hi = mid; }
        }
        const int64_t p = lo;
        const bool ok = (p == 0 || memcmp(row, ref_a.data(), p*sizeof(T)) == 0) &&
                        (p == n_cols || memcmp(row + p, ref_b.data(), (n_cols - p)*sizeof(T)) == 0);
        if (!ok) {
            ggml_backend_tensor_clear_input_mask_hint(dst);
            return false;
        }
        prefix[i] = (int32_t) p;
    }
    ggml_backend_tensor_set_input_mask_hint(dst, prefix.data(), n_rows, n_cols, &a, &b);
    return true;
}
