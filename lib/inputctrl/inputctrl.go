package inputctrl

import (
	"bufio"
	"fmt"
	"os"
	"strings"

	"msh/lib/debugctrl"
	"msh/lib/servctrl"
)

// GetInput is used to read input from user.
// [goroutine]
func GetInput() {
	var line string
	var err error

	reader := bufio.NewReader(os.Stdin)

	for {
		line, err = reader.ReadString('\n')
		if err != nil {
			debugctrl.Logln("GetInput:", err)
			continue
		}

		// make sure that only 1 space separates words
		line = strings.ReplaceAll(line, "\n", "")
		line = strings.ReplaceAll(line, "\r", "")
		line = strings.ReplaceAll(line, "\t", " ")
		for strings.Contains(line, "  ") {
			line = strings.ReplaceAll(line, "  ", " ")
		}
		lineSplit := strings.Split(line, " ")

		debugctrl.Logln("GetInput: user input:", lineSplit[:])

		switch lineSplit[0] {
		// target msh
		case "msh":
			// check that there is a command for the target
			if len(lineSplit) < 2 {
				fmt.Println("msh command error: specify msh command")
				continue
			}

			switch lineSplit[1] {
			case "start":
				err = servctrl.StartMinecraftServer()
				if err != nil {
					debugctrl.Logln("GetInput:", err)
				}
			case "freeze":
				// stop minecraft server forcefully
				err = servctrl.StopMinecraftServer(true)
				if err != nil {
					debugctrl.Logln("GetInput:", err)
				}
			default:
				fmt.Println("msh command error: unknown command (start - freeze)")
			}

		// taget minecraft server
		case "mine":
			// check that there is a command for the target
			if len(lineSplit) < 2 {
				fmt.Println("msh command error: specify mine command")
				continue
			}

			// just pass the command to the minecraft server terminal
			_, err = servctrl.ServTerminal.Execute(strings.Join(lineSplit[1:], " "), "user input")
			if err != nil {
				debugctrl.Logln("GetInput:", err)
			}

		// wrong target
		default:
			fmt.Println("please specify the target (msh - mine)")
		}
	}
}
