def process_cmd(command, identifier, options=None):
    result = ""
    if command == "help":
        pass
    elif command in ["usecontext"]:
        pass
    elif command in ["useeffect"]:
        pass
    elif command in ["usestate"]:
        # perlu gunakan options utk tipe data agar bisa kasih initial value
        capid = identifier.capitalize()
        setcapid = "set" + capid
        initial_value = "[]"
        template = f"const [{identifier}, {setcapid}] = useState({initial_value})"
        result = template
    elif command in "useselector":
        pass
    elif command in ["fc", "stateless", "functional component"]:
        pass
    elif command in ["cc", "statefull", "class component"]:
        pass
    return result
