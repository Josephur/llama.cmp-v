#pragma once

// Runtime research selectors.
//
// Research-only feature switches in this fork are environment variables read once at
// process start. To A/B variants on one loaded model, a selector may instead be read through
// ggml_research_getenv(): it returns a runtime override when one was set with
// ggml_research_set(), and the process environment otherwise. Callers must not cache the
// result across graph computes when they want to be switchable.
//
// Deliberately tiny and self-contained (one header, one source file, no dependency on the
// rest of ggml) so it survives upstream llama.cpp updates as an additive file.

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

// returns the override for `name` if set, else getenv(name); NULL when neither exists.
// the returned pointer stays valid until the next ggml_research_set() for that name.
const char * ggml_research_getenv(const char * name);

// integer convenience: atoi() of ggml_research_getenv(name), or `def` when unset
int ggml_research_getenv_int(const char * name, int def);

// set (value != NULL) or clear (value == NULL) a runtime override
void ggml_research_set(const char * name, const char * value);

// monotonically increasing counter, bumped by every ggml_research_set(); callers that cache
// a selector value can compare this to decide when to re-read
uint64_t ggml_research_generation(void);

// Activation reporting.
//
// Every selector read through this header is recorded. A selector that a deployment sets but
// that no surviving code reads is invisible otherwise: an unknown environment variable is
// silent, and same-package A/B testing cannot see code missing from both arms. This is how the
// PINNED_SNAPSHOT / MAPPED_HOST_PREFILL / SSM_CONV_STATE_FUSION family stayed "enabled" in the
// systemd unit for three weeks after a re-base dropped it (2026-09-04).
//
// Returns a JSON object as a NUL-terminated string owned by the library:
//   {"read":[{"name":..,"value":..,"present":0|1,"reads":N}, ...]}
// `present` is whether a value existed at first read (override or environment).
// The caller must not free it; it stays valid until the next call.
const char * ggml_research_activation_report(void);

// 1 when `name` has been read at least once through this header, else 0.
int ggml_research_was_read(const char * name);

#ifdef __cplusplus
}

#include <atomic>

// Thread-safe cached selector read. Selector values are stable for the life of a
// generation, so hot paths must not pay the registry lock on every call: cache the
// value and re-read only when ggml_research_set() bumps the generation.
//
//   static ggml_research_cached_int sel;
//   if (sel.get("GGML_CUDA_SOMETHING", 0)) { ... }
struct ggml_research_cached_int {
    std::atomic<uint64_t> gen{UINT64_MAX};
    std::atomic<int>      val{0};

    int get(const char * name, int def) {
        const uint64_t g = ggml_research_generation();
        if (gen.load(std::memory_order_acquire) != g) {
            const int v = ggml_research_getenv_int(name, def);
            val.store(v, std::memory_order_relaxed);
            gen.store(g, std::memory_order_release);
            return v;
        }
        return val.load(std::memory_order_relaxed);
    }
};
#endif
