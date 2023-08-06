from .dotlang import dotlang
import datetime

def timestamp(time_format="%Y%m%d_%H%M%S"):
	return datetime.datetime.now().strftime(time_format)

def main():
    code = 1
    while code != "x":
        try:
            prompt = datetime.datetime.utcnow().isoformat()
            code = input(f"DOTLANG {prompt} >> ")
            code = code.strip()
            if code != "" and code != "x":
                dotlang(code, output_file='dotlang_' + timestamp())
        except EOFError as eof:
            print("Ctrl+D? Exiting...", eof)
            break
        except Exception as err:
            print(err)
    

if __name__ == "__main__":
    main()
