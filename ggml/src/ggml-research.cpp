#include "ggml-research.h"

#include <atomic>
#include <cstdlib>
#include <map>
#include <mutex>
#include <string>

namespace {
struct research_read {
    std::string value;
    bool        present = false;
    uint64_t    reads   = 0;
};
std::mutex &                        research_mutex()    { static std::mutex m; return m; }
std::map<std::string, std::string> & research_overrides() { static std::map<std::string, std::string> m; return m; }
std::map<std::string, research_read> & research_reads()   { static std::map<std::string, research_read> m; return m; }
std::atomic<uint64_t>               research_gen{0};

void research_note_read(const char * name, const char * value) {
    std::lock_guard<std::mutex> lock(research_mutex());
    research_read & r = research_reads()[name];
    r.present = value != nullptr;
    r.value   = value != nullptr ? value : "";
    r.reads  += 1;
}

void research_json_escape(std::string & out, const std::string & in) {
    for (const char c : in) {
        switch (c) {
            case '"':  out += "\\\""; break;
            case '\\': out += "\\\\"; break;
            case '\n': out += "\\n";  break;
            case '\r': out += "\\r";  break;
            case '\t': out += "\\t";  break;
            default:
                if ((unsigned char) c < 0x20) { out += ' '; } else { out += c; }
        }
    }
}
}

const char * ggml_research_getenv(const char * name) {
    if (name == nullptr) {
        return nullptr;
    }
    const char * result = nullptr;
    {
        std::lock_guard<std::mutex> lock(research_mutex());
        auto & overrides = research_overrides();
        auto it = overrides.find(name);
        if (it != overrides.end()) {
            result = it->second.c_str();
        }
    }
    if (result == nullptr) {
        result = std::getenv(name);
    }
    research_note_read(name, result);
    return result;
}

const char * ggml_research_activation_report(void) {
    static std::string report;
    std::string out = "{\"read\":[";
    {
        std::lock_guard<std::mutex> lock(research_mutex());
        bool first = true;
        for (const auto & [name, r] : research_reads()) {
            if (!first) { out += ","; }
            first = false;
            out += "{\"name\":\"";
            research_json_escape(out, name);
            out += "\",\"value\":\"";
            research_json_escape(out, r.value);
            out += "\",\"present\":";
            out += r.present ? "1" : "0";
            out += ",\"reads\":";
            out += std::to_string(r.reads);
            out += "}";
        }
    }
    out += "]}";
    report = std::move(out);
    return report.c_str();
}

int ggml_research_was_read(const char * name) {
    if (name == nullptr) {
        return 0;
    }
    std::lock_guard<std::mutex> lock(research_mutex());
    return research_reads().count(name) ? 1 : 0;
}

int ggml_research_getenv_int(const char * name, int def) {
    const char * value = ggml_research_getenv(name);
    return value != nullptr ? std::atoi(value) : def;
}

void ggml_research_set(const char * name, const char * value) {
    if (name == nullptr) {
        return;
    }
    std::lock_guard<std::mutex> lock(research_mutex());
    auto & overrides = research_overrides();
    if (value == nullptr) {
        overrides.erase(name);
    } else {
        overrides[name] = value;
    }
    research_gen.fetch_add(1, std::memory_order_relaxed);
}

uint64_t ggml_research_generation(void) {
    return research_gen.load(std::memory_order_relaxed);
}
