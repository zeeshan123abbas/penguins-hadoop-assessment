"""Runs commands as maria_dev on the sandbox and records a real terminal transcript."""
import subprocess, sys, json, os

PROMPT = "[maria_dev@sandbox-hdp ~]$ "

def run(name, cmds, cwd="/home/maria_dev", stdin_files=None):
    out = []
    for c in cmds:
        out.append(PROMPT + c)
        p = subprocess.run(
            ["sudo", "-u", "maria_dev", "bash", "-c",
             f"source /opt/bd/env.sh; cd {cwd}; {c}"],
            capture_output=True, text=True)
        text = (p.stdout + p.stderr)
        lines = [l for l in text.splitlines() if "unable to resolve host" not in l]
        out.extend(lines)
    out.append(PROMPT)
    os.makedirs("logs", exist_ok=True)
    with open(f"logs/{name}.txt", "w") as f:
        f.write("\n".join(out) + "\n")
    print("\n".join(out))

if __name__ == "__main__":
    spec = json.load(open(sys.argv[1]))
    for item in spec:
        run(item["name"], item["cmds"], item.get("cwd", "/home/maria_dev"))
