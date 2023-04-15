import matplotlib.pyplot as plt


sizes = []
times = []
lineNumber = 1
file1 = open("results.txt","r")
for line in file1:
    if(lineNumber % 2 == 1):
        sizes.append(float(line))
    else:
        rtime, memusg = line.split(" ")
        times.append(float(rtime))
    lineNumber= lineNumber+1
file1.close()


plt.plot(sizes, times)
plt.title("Approve-publish, in MonPoly")
plt.xlabel("size")
plt.ylabel("time")
plt.show()
plt.savefig('MonPoly.png')
