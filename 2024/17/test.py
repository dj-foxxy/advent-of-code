
v = 0o24127545135503300
print(v)

value = [2,4,1,2,7,5,4,5,1,3,5,5,0,3,3,0]
value.reverse()
s = f'0o{''.join(map(str, value))}'
print(s)
print(int(s, 8))
