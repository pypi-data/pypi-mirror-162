import os

def Basedir(path:str) -> str:
    return os.path.dirname(path)

def Join(*path) -> str:
    return os.path.join(*path)

def Exists(path:str) -> bool:
    return os.path.exists(path)

if __name__ == "__main__":
    print(Join("a", "b"))