max = 101325
min = 95000
diff = max - min
fout = open("sim_data.csv", "w")
for i in range(60):
    fout.write(str(max - diff * i / 60) + "\n")

for i in range(55):
    fout.write(str(min + diff * i / 60) + "\n")

fout.close()