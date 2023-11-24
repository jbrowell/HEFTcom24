# Use this script to generate a dependency file for unix-based systems.
# The code that will remove the builds from the packages included in environment_v1.0.yml file.
# The new file will be called environment_v1.0_unix.yml.
# Any depdn
with open("environment.yml", "r") as env, open("environment_unix.yml", "w") as new_env:
    lines = env.readlines()
    i, n = 0, len(lines)

    # Find the dependencies section.
    while i < n:
        line = lines[i]
        i += 1
        if "dependencies:" in line:
            break

    # Dependencies that seem to only exist on windows:
    windows_only = [
        "icc_rt",
        "pywin32",
        "vc",
        "vs2015_runtime",
        "win_inet_pton"
    ]
    def isWindowsOnly(line):
        for dep in windows_only:
            if (" " + dep) in line:
                return True
        return False

    # Remove the builds from the dependencies section
    while i < n:
        line = lines[i]
        if "pip:" in line or line[0] != ' ':
            break
        sections = line.split("=")
        if isWindowsOnly(line):
            lines[i] = ""
        elif len(sections) > 2:
            lines[i] = line[0:-(len(sections[-1]) + 1)] + "\n"
        i += 1

    # Remove the prefix section.
    while i < n:
        line = lines[i]
        if "prefix:" in line:
            lines[i] = ""
            i += 1
            break
        i += 1
    
    # Write lines to new environment file.
    new_env.writelines(lines)