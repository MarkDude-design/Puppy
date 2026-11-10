/* Puppf sandbox — static agent-core, round 3 (received 2026-11-10, verbatim).
 * Source: Gemini seat via MarkDude; copy on the bus: sandbox/incoming/gemini-agent-core-round3-2026-11-10.md
 * Compiled statically on the runner by .github/workflows/sandbox-build.yml (Z compile step, round 3).
 */
#include <stdio.h>
#include <unistd.h>
#include <sys/sysinfo.h>

int main() {
    struct sysinfo info;
    sysinfo(&info);

    printf("\n=== PUPPF AGENT-CORE [ONLINE] ===\n");
    printf("[agent] PID: %d\n", getpid());
    printf("[agent] Uptime: %ld seconds\n", info.uptime);
    printf("[agent] Free RAM: %ld MB\n", info.freeram / 1024 / 1024);
    printf("[agent] Status: Initialized successfully within minimal RAM OS.\n");
    printf("===================================\n");

    return 0;
}
