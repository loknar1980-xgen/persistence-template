# System Memory — Prose Format

## Python Configuration
The Python executable is located at C:\Users\me\AppData\Roaming\uv\python\cpython-3.13.10-windows-x86_64-none\python.exe. Note that the default Python installation is broken due to a Miniconda conflict in the Pinokio environment. You should always use a virtual environment or specify the full path when running Python scripts.

## Network Configuration
The NAS device is at IP address 192.168.2.3 with hostname MyNAS. The primary network interface is on 192.168.2.2 (Intel adapter, metric 10) and the secondary interface is on 192.168.2.10 (Marvell adapter, metric 50). The main gateway is at 192.168.0.1 which is a CenturyLink router that performs the first NAT. The local gateway is at 192.168.2.1 which is a secondary router performing the second NAT. For SMB connections, you should use the hostname path //MyNAS/data/ as the primary connection method, with the IP path //192.168.2.3/data/ as a fallback. If the NAS disappears from the network, the fix is to power cycle the gateway.

## LM Studio Configuration
LM Studio is running at http://localhost:1234 and is version 0.4.6 of the GUI. The API key is sk-lm-example-key. The CLI tool lms should only be run from cmd, not PowerShell. Note that the lms get command stalls in non-terminal contexts, so use curl for HuggingFace downloads instead. The models are stored on the F drive at F:\AI_Models. There is a junction from C:\Users\me\.lmstudio\models\lmstudio-community to F:\AI_Models\lmstudio-community. Currently loaded models include Google Gemma 3 12B (loaded, used as the stock agent VLM with context length 4096, quantized to Q4_K_M, size 7.3 GB) and Nvidia Nemotron 3 Nano 4B (loaded, used as the local mind model with context length 16384, quantized to Q4_K_M, size 2.8 GB). Available but not loaded models include Google Gemma 3 27B (context length 8192, QAT Q4_0 quantization, size 16.4 GB).
