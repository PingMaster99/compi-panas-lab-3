.data
first_number: .word 11
second_number: .word 77



.text
.globl main


    
main:
    # GCD
    lw $a0, first_number 
    lw $a1, second_number
    jal GCD

    # PRINT
    move $a0, $v0 
    li $v0,1
    syscall

    # HALT
    li $v0, 10 
    syscall


GCD:
    # Sack (size, RA, params)
    addi $sp, $sp, -12	# 12 bytes (1 RA, 2 Params)
    sw $ra, 0($sp)
    sw $s0, 4($sp)
    sw $s1, 8($sp)

    move $s0, $a0
    move $s1, $a1

    beq $s1, $zero, returnGCD

    move $a0, $s1
    div $s0, $s1
    mfhi $a1

    jal GCD		# Saves the return addess * next instruction *



exitGCD:
    # Get stack values
    lw $ra, 0 ($sp)
    lw $s0, 4 ($sp)
    lw $s1, 8 ($sp)
    addi $sp,$sp , 12
    jr $ra		# Gives back control to original caller

returnGCD:
    move $v0, $s0
    j exitGCD