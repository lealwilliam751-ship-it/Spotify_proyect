from pathlib import Path
import os

print(f"File: {__file__}")
print(f"Resolve: {Path(__file__).resolve()}")
print(f"Parent: {Path(__file__).resolve().parent}")
print(f"P2: {Path(__file__).resolve().parent.parent}")
print(f"P3: {Path(__file__).resolve().parent.parent.parent}")
print(f"P4: {Path(__file__).resolve().parent.parent.parent.parent}")
print(f"Exists .env there?: {(Path(__file__).resolve().parent.parent.parent.parent / '.env').exists()}")
