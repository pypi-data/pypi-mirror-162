# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pyquil_for_azure_quantum']

package_data = \
{'': ['*']}

install_requires = \
['azure-quantum>=0.25.218240,<0.26.0',
 'lazy-object-proxy>=1.7.1,<2.0.0',
 'numpy>=1.21.6,<2.0.0',
 'pyquil>=3.1.0,<4.0.0',
 'scipy>=1.6.1,<2.0.0',
 'wrapt>=1.14.0,<2.0.0']

setup_kwargs = {
    'name': 'pyquil-for-azure-quantum',
    'version': '0.0.2',
    'description': 'Run Quil programs on Microsoft Azure Quantum using pyQuil',
    'long_description': '# pyquil-for-azure-quantum\n\nThis library allows you to use [pyQuil] to run programs on [Azure Quantum](https://azure.microsoft.com/en-us/services/quantum/) against Rigetti targets. Internally, it leverages the [azure-quantum] package.\n\n## Usage\n\nGenerally, you use [pyQuil] normally, with a few differences:\n\n1. Instead of `pyquil.get_qc()`, you will use either `pyquil_azure_quantum.get_qvm()` or `pyquil_azure_quantum.get_qpu()`.\n2. You do not need to have `qvm` or `quilc` running in order to run programs through `pyquil_azure_quantum`. You may still run them if you wish to run QVM locally instead of passing through Azure or if you wish to precompile your programs (e.g., to inspect the exact Quil that will run).\n3. You do not need a QCS account or credentials unless you wish to manually inspect the details of the QPU (e.g., list all qubits).\n4. You **must** have these environment variables set:\n   1. `AZURE_QUANTUM_SUBSCRIPTION_ID`: The Azure subscription ID where the Quantum Workspace is located.\n   2. `AZURE_QUANTUM_WORKSPACE_RG`: The Azure resource group where the Quantum Workspace is located. \n   3. `AZURE_QUANTUM_WORKSPACE_NAME`: The name of the Quantum Workspace.\n   4. `AZURE_QUANTUM_WORKSPACE_LOCATION`: The region where the Quantum Workspace is located.\n5. You **may** [set environment variables][azure auth] to authenticate with Azure. If you do not, a browser will open to the Azure portal to authenticate.\n6. Whenever possible, you should prefer using `AzureQuantumComputer.run_batch()` over `Program.write_memory(); AzureQuantumComputer.run()` to run programs which have multiple parameters. Calling `write_memory()` followed by `run()` will still work but will be much slower than running a batch of parameters all at once.\n\n\n## Examples\n\n### 1. Leveraging Hosted QVM and quilc\n\nWith this program, you do not need to run `qvm` nor `quilc` locally in order to leverage them, as they can run through Azure Quantum.\n\n```python\nfrom pyquil_for_azure_quantum import get_qpu, get_qvm\nfrom pyquil.gates import CNOT, MEASURE, H\nfrom pyquil.quil import Program\nfrom pyquil.quilbase import Declare\n\nprogram = Program(\n    Declare("ro", "BIT", 2),\n    H(0),\n    CNOT(0, 1),\n    MEASURE(0, ("ro", 0)),\n    MEASURE(1, ("ro", 1)),\n).wrap_in_numshots_loop(1000)\n\nqpu = get_qpu("Aspen-11")\nqvm = get_qvm()\n\nexe = qpu.compile(program)  # This does not run quilc yet.\nresults = qpu.run(exe)  # Quilc will run in the cloud before executing the program.\nqvm_results = qvm.run(exe)  # This runs the program on QVM in the cloud, not locally.\n```\n\n### 2. Running quilc Locally\n\nYou can optionally run quilc yourself and disable the use of quilc in the cloud.\n\n```python\nfrom pyquil_for_azure_quantum import get_qpu\nfrom pyquil.gates import CNOT, MEASURE, H\nfrom pyquil.quil import Program\nfrom pyquil.quilbase import Declare\n\n\nprogram = Program(\n    Declare("ro", "BIT", 2),\n    H(0),\n    CNOT(0, 1),\n    MEASURE(0, ("ro", 0)),\n    MEASURE(1, ("ro", 1)),\n).wrap_in_numshots_loop(1000)\nqpu = get_qpu("Aspen-11")\nnative_quil = qpu.compiler.quil_to_native_quil(program)  # quilc must be running locally to compile\nexe = qpu.compile(native_quil, to_native_gates=False)  # Skip quilc in the cloud\nresults = qpu.run(exe)\n```\n\n### 3. Running Parametrized Circuits in a Batch\n\nWhen you have a program which should be run across multiple parameters, you can submit all the parameters at once to significantly improve performance.\n\n```python\nimport numpy as np\nfrom pyquil_for_azure_quantum import get_qpu\nfrom pyquil.gates import MEASURE, RX\nfrom pyquil.quil import Program\nfrom pyquil.quilbase import Declare\nfrom pyquil.quilatom import MemoryReference\n\n\nprogram = Program(\n    Declare("ro", "BIT", 1),\n    Declare("theta", "REAL", 1),\n    RX(MemoryReference("theta"), 0),\n    MEASURE(0, ("ro", 0)),\n).wrap_in_numshots_loop(1000)\n\nqpu = get_qpu("Aspen-11")\ncompiled = qpu.compile(program)\n\nmemory_map = {"theta": [[0.0], [np.pi], [2 * np.pi]]}\nresults = qpu.run_batch(compiled, memory_map)  # This is a list of results, one for each parameter set.\n\nresults_0 = results[0].readout_data["ro"]\nresults_pi = results[1].readout_data["ro"]\nresults_2pi = results[2].readout_data["ro"]\n```\n\n> Microsoft, Microsoft Azure, and Azure Quantum are trademarks of the Microsoft group of companies. \n\n[azure-quantum]: https://github.com/microsoft/qdk-python\n[pyQuil]: https://pyquil-docs.rigetti.com/en/stable/\n[azure auth]: https://docs.microsoft.com/en-us/azure/quantum/optimization-authenticate-service-principal#authenticate-as-the-service-principal\n',
    'author': 'Dylan Anthony',
    'author_email': 'danthony@rigetti.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/rigetti/pyquil-for-azure-quantum',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<3.11',
}


setup(**setup_kwargs)
