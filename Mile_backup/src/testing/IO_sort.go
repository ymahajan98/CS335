package main

import "fmt"

func main() {
	var b [100]int
	len := 100
	for i := 0; i < len; i++ {
		d := 0
		scan b[i]
	}

	for i := 0; i < len; i = i + 1 {
		for j := 0; j < (len-1); j = j + 1 {
			if b[j] > b[j+1] {
				c := b[j]
				b[j] = b[j+1]
				b[j+1] = c
			}
		}
	}

	for i := 0; i < len; i = i + 1 {
		print b[i]," "
	}
	print "\n"
}
