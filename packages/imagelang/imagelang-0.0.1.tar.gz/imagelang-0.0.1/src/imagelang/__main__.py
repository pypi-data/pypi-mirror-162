from .imagelang import imagelang
import datetime


def main():
    code = 1
    while code != "x":
        try:
            prompt = datetime.datetime.utcnow().isoformat()
            code = input(f"IMAGELANG {prompt} >> ")
            code = code.strip()
            if code != "" and code != "x":
                imagelang(code)
        except EOFError as eof:
            print("Exiting...", eof)
            break
        except Exception as err:
            print(err)

if __name__ == "__main__":
    main()
