from .tviewlang import tviewlang
import datetime


def main():
    code = 1
    while code != "x":
        try:
            prompt = datetime.datetime.utcnow().isoformat()
            code = input(f"TVIEWLANG {prompt} >> ")
            code = code.strip()
            if code != 'x':
                if code == 'sample':
                    tviewlang()
                elif code:
                    tviewlang(code)                
        except EOFError as eof:
            print("Exiting...", eof)
            break
        except Exception as err:
            print(err)


if __name__ == "__main__":
    main()
