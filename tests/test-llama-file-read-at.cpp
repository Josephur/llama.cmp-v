#include "llama-mmap.h"

#include <algorithm>
#include <atomic>
#include <chrono>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <stdexcept>
#include <thread>
#include <vector>

int main() {
    constexpr size_t file_size = 8 * 1024 * 1024;
    constexpr size_t read_size = 256 * 1024;

    std::vector<uint8_t> expected(file_size);
    for (size_t i = 0; i < expected.size(); ++i) {
        expected[i] = (uint8_t) ((i * 131 + i / 97) & 0xff);
    }

    const auto nonce = std::chrono::high_resolution_clock::now().time_since_epoch().count();
    const auto path  = std::filesystem::temp_directory_path() / ("llama-read-at-" + std::to_string(nonce) + ".bin");
    {
        std::ofstream output(path, std::ios::binary);
        output.write((const char *) expected.data(), expected.size());
        if (!output.good()) {
            throw std::runtime_error("failed to create positional-read fixture");
        }
    }

    try {
        llama_file               file(path.string().c_str(), "rb");
        std::vector<std::thread> readers;
        std::atomic<bool> mismatch{false};
        for (size_t worker = 0; worker < 8; ++worker) {
            readers.emplace_back([&, worker] {
                std::vector<uint8_t> actual(read_size);
                for (size_t iteration = 0; iteration < 64; ++iteration) {
                    const size_t offset = (worker * 97777 + iteration * 131071) % (file_size - read_size);
                    file.read_raw_at_unsafe(actual.data(), actual.size(), offset);
                    if (!std::equal(actual.begin(), actual.end(), expected.begin() + offset)) {
                        mismatch.store(true, std::memory_order_relaxed);
                        return;
                    }
                }
            });
        }
        for (auto & reader : readers) {
            reader.join();
        }
        if (mismatch.load(std::memory_order_relaxed)) {
            throw std::runtime_error("concurrent positional read returned incorrect data");
        }
    } catch (...) {
        std::filesystem::remove(path);
        throw;
    }

    std::filesystem::remove(path);
    return 0;
}
