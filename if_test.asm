
asect 0x00


ldi r0, 6
ldi r1, 7

if 
cmp r0, r1
is eq
ldi r0, 1
else 
ldi r0, 2
fi

ldi r3, 0
st r3, r0



ldi r0, 8
ldi r1, 8

if
cmp r0, r1
is eq
ldi r0, 1
else 
ldi r0, 2
fi

ldi r3, 1
st r3, r0


halt
end

# asect 0x00
# num: dc 0

# ldi r0, num
# ldc r0, r0
# if
#     tst r0
# is z
#     ldi r0, 175
# fi

# halt
# end


# asect 0x00


# ldi r0, 6
# ldi r1, 7


# if 
# cmp r0, r1
# is eq
# ldi r0, 1
# else 
# ldi r0, 2
# fi

# ldi r3, 0
# st r3, r0



# ldi r0, 8
# ldi r1, 8

# if
# cmp r0, r1
# is eq
# ldi r0, 1
# else 
# ldi r0, 2
# fi

# ldi r3, 1
# st r3, r0


# halt
# end