## roll-call
<p>Built with the following tools and technologies:</p>
<p>
	<img src="https://img.shields.io/badge/Python-3776AB.svg?style=flat-square&logo=Python&logoColor=white" alt="Python">
	<img src="https://img.shields.io/badge/Poetry-60A5FA.svg?style=flat-square&logo=Poetry&logoColor=white" alt="Poetry">
</p>  

## Demo
<img src="https://github.com/inth3wild/roll-call/blob/main/demo.gif" alt="Roll Call Demo">


## Code Overview
The script performs the following actions:
1. Connects with a biometric attendance device.
2. Retrieve attendance records for a specific student.
3. Identify days where the student hasn't signed in.
4. Optionally, manipulate the device's date and time to allow the student to sign in for previous days.

##  Project Structure
```sh
└── roll-call/
    ├── README.md
    ├── poetry.lock
    ├── pyproject.toml
    ├── roll_call.py
    └── settings
        └── config.py
```
