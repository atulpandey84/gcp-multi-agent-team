import argparse
from .workflows.engineering import run

def main():
    p = argparse.ArgumentParser()
    p.add_argument("objective", nargs="?", default="Create a GCP Landing Zone application environment using Terraform with security, FinOps, testing and operational controls.")
    args = p.parse_args()
    result = run(args.objective)
    print("\n=== ENGINEERING ORCHESTRATOR ===\n")
    print(result.get("final_response", "No response returned."))

if __name__ == "__main__":
    main()
