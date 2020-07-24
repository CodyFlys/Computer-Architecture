"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        self.pc = 0 # program counter
        self.running = False
        self.LDI = 0b10000010 # set the value of a register to a integer(130)
        self.PRN = 0b01000111 # Print numeric value stored in the given register
        self.HLT = 0b00000001 # Halt the CPU (and exit the emulator)
        self.MUL = 0b10100010 # Multiply the values in two registers together and store the result in registerA.
        self.POP = 0b01000110 # POP
        self.PUSH = 0b01000101 # PUSH
        self.reg[7] = 0xF4
        self.CALL = 0b01010000
        self.RET = 0b00010001
        self.ADD = 0b10100000
        self.JMP = 0b01010100
        self.JEQ = 0b01010101
        self.JNE = 0b01010110
        self.flag = 0b00000000
        self.CMP = 0b10100111

    def ram_read(self, mar):
        return self.ram[mar] # return our memory address register

    def ram_write(self, mar, mdr):
        self.ram[mar] = mdr # write a memory address register that has a value (mdr) = memory data register

    def load(self):
        """Load a program into memory."""
        address = 0

        if len(sys.argv) != 2:
            print("usage: ls8.py filename")
            sys.exit(1)

        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    value = line.split("#")[0].strip()
                    if value == '':
                        continue
                    v = int(value, 2)
                    self.ram[address] = v
                    address += 1
        except FileNotFoundError:
            print(f"Error {sys.argv[1]}")
            sys.exit(1)

        # address = 0

        # # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000, # 0
        #     0b00001000, # 8
        #     0b01000111, # PRN R0
        #     0b00000000, # 0
        #     0b00000001, # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]

        # `FL` bits: `00000LGE`
        elif op == "CMP":
            # EQUAL
            if self.reg[reg_a] == self.reg[reg_b]:
                self.flag = 0b00000001
            
            # LESS THAN
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.flag = 0b00000100

            # GREATER THAN
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.flag = 0b00000010
            else:
                self.flag = 0b00000000
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        # set CPU to running
        running = True
        while running:
            # Setting ir to be whatever program we're running from ram
            ir = self.ram[self.pc]

            # print(reg_a)
            reg_a = self.ram_read(self.pc + 1)
            # print(reg_b)
            reg_b = self.ram_read(self.pc + 2)

            # if ir == load immediate (LDI)
            if ir == self.LDI:
                # create a variable(register_number) from ram at address #0
                register_number = self.ram[self.pc+1]
                # create a variable(value), from ram at address 3 which is 8
                value = self.ram[self.pc+2] # value = 8
                self.reg[register_number] = value
                # print(self.reg)
                self.pc += 3
                # print(f'REGISTER NUMBER: {register_number} VALUE: {value}')

            elif ir == self.PRN:
                register_number = self.ram[self.pc+1]
                print(self.reg[register_number])
                self.pc +=2

            # halting CPU
            elif ir == self.HLT:
                running = False
                self.pc +=1

            elif ir == self.MUL:
                self.alu("MUL", reg_a, reg_b)
                self.pc += 3

            elif ir == self.PUSH:
                # decrement sp by 1
                self.reg[7] -= 1
                self.reg[7] &= 0xff
                # set sp pos in ram to be registry value of ram at next instruction
                self.ram[self.reg[7]] = self.reg[self.ram[self.pc+1]]
                self.pc += 2
                print(self.ram)

            elif ir == self.POP:
                self.reg[self.ram[self.pc+1]] = self.ram[self.reg[7]]
                self.reg[7] += 1
                self.reg[7] &= 0xff
                self.pc += 2

            elif ir == self.CALL:
                # looking ahead in the ir
                returnAddress = self.pc + 2
                # decrement sp
                self.reg[7] -= 1
                # setting sp in ram to be what we looked ahead to
                self.ram[self.reg[7]] = returnAddress
                self.pc = self.reg[self.ram[self.pc+1]]

            elif ir == self.RET:
                # return address set to sp in ram
                returnAddress = self.ram[self.reg[7]]
                # setting reg in ram at next ir to be current ram sp
                self.reg[self.ram[self.pc+1]] = self.ram[self.reg[7]]
                # Increment stack pointer
                self.reg[7] += 1
                # self.pc becomes the return address we set
                self.pc = returnAddress

            elif ir == self.ADD:
                self.alu("ADD", reg_a, reg_b)
                self.pc += 3



            # SPRINT ----
            elif ir == self.CMP:
                self.alu("CMP", reg_a, reg_b)
                self.pc += 3
                # print("CMP")


            # Jump to the address stored in the given register.
            # Set the `PC` to the address stored in the given register.
            elif ir == self.JMP:
                # self.pc becomes the register in ram at self.pc+1 to land on the correct spot I believe line 75 of the IR file
                self.pc = self.reg[self.ram[self.pc + 1]]
                # print("JMP")

            # If `equal` flag is set (true), jump to the address stored in the given register.
            elif ir == self.JEQ:
                # check if flag is 1
                if self.flag == 0b00000001:
                    # if it is i go to the register in ram at pc +1
                    self.pc = self.reg[self.ram[self.pc + 1]]
                else:
                    self.pc += 2

            # If `E` flag is clear (false, 0), jump to the address stored in the given register.
            elif ir == self.JNE:
                # here I check if the flag is not equal to 1 so that my alu will work easier.
                if self.flag != 0b00000001:
                    # if it isn't 1 we will go to reg in ram at pc +1
                    self.pc = self.reg[self.ram[self.pc + 1]]
                    # print("JNE")
                else:
                    self.pc += 2

            
            else:
                print(f'Unkown instruction {ir} at address {self.pc}')
                sys.exit(1)