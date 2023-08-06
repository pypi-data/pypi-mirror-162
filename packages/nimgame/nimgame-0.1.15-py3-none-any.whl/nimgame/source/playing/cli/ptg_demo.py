"""Dummy docstring"""



def ptgdemo():
    with ptg.WindowManager() as manager:
       demo = ptg.Window(
          ptg.Label("[210 bold]Hello world!"),
          ptg.Label(),
          ptg.InputField(prompt="Who are you?"),
          ptg.Label(),
          ptg.Button("Submit!")
       )
       
       manager.add(demo)
       manager.run()


if __name__ == '__main__':
    # An empty command seems to make the Windows cmd terminal capable of ANSI.
    # Note that importing pytermgui seems to emit an ESC[14t (setting maximum
    # number of lines in window to 14). In order to get this interpreted, the
    # empty command must be done BEFORE importing pytermgui
    import os; os.system('')

    import pytermgui as ptg
    
    ptgdemo()
