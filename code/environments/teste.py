# import numpy as np

# solved = np.array([ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53])
# state =  np.array([ 6, 3, 0, 7, 4, 1, 8, 5, 2, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 47, 21, 22, 50, 24, 25, 53, 27, 28, 38, 30, 31, 41, 33, 34, 44, 36, 37, 20, 39, 40, 23, 42, 43, 26, 45, 46, 29, 48, 49, 32, 51, 52, 35])

# cross = np.array([1,3,4,5,7])

# for face in range(0,54,9):
#     i = cross + face
#     print(state[i] == solved[i])


# WHITE:0 - U, YELLOW:1 - D, BLUE:2 - L, GREEN:3 - R, ORANGE: 4 - B, RED: 5 - F

import numpy as np

# solved = np.array([ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53])
# state =  np.array([ 6, 3, 0, 7, 4, 1, 8, 5, 2, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 47, 21, 22, 50, 24, 25, 53, 27, 28, 38, 30, 31, 41, 33, 34, 44, 36, 37, 20, 39, 40, 23, 42, 43, 26, 45, 46, 29, 48, 49, 32, 51, 52, 35])
solved = np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 5]])
state = np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 5, 2, 2, 5, 2, 2, 5, 3, 3, 4, 3, 3, 4, 3, 3, 4, 4, 4, 2, 4, 4, 2, 4, 4, 2, 5, 5, 3, 5, 5, 3, 5, 5, 3]])

face = np.array([1,2,3,4,5,6,7])

d = {}
d['branco'] = face + 9*0
d['amarelo'] = face + 9*1
d['azul'] = face + 9*2
d['verde'] = face + 9*3
d['laranja'] = face + 9*4
d['vermelho'] = face + 9*5

# print(solved[d['vermelho']])




# cross['branco'] = [1,3,4,5,7,13,22,23,31,32,40,41,49,50]
# cross['amarelo'] = [4,10,12,13,14,16,21,22,30,31,39,40,48,49]
# cross['azul'] = [4,7,13,16,22,28,30,31,32,34,37,40,49,52]
# cross['verde'] = [1,4,10,13,19,21,22,23,25,31,40,43,46,49]
# cross['laranja'] = [4,5,12,13,19,22,31,34,37,39,40,41,43,49]
# cross['vermelho'] = [3,4,13,14,22,25,28,31,40,46,48,49,50,52]


cross = np.array([6],dtype=int)

cross[0] = np.array([1,3,4,5,7,13,22,23,31,32,40,41,49,50],dtype=int)
cross[1] = np.array([4,10,12,13,14,16,21,22,30,31,39,40,48,49],dtype=int)
cross[2] = np.array([1,4,10,13,19,21,22,23,25,31,40,43,46,49],dtype=int)
cross[3] = np.array([4,7,13,16,22,28,30,31,32,34,37,40,49,52],dtype=int)
cross[4] = np.array([4,5,12,13,19,22,31,34,37,39,40,41,43,49],dtype=int)
cross[5] = np.array([3,4,13,14,22,25,28,31,40,46,48,49,50,52],dtype=int)




self.crossIndex = np.array([[1,3,4,5,7,13,22,23,31,32,40,41,49,50]], dtype=int) 
self.crossIndex = np.append(self.crossIndex, [[4,10,12,13,14,16,21,22,30,31,39,40,48,49]], axis=0)
self.crossIndex = np.append(self.crossIndex, [[1,4,10,13,19,21,22,23,25,31,40,43,46,49]], axis=0)
self.crossIndex = np.append(self.crossIndex, [[4,7,13,16,22,28,30,31,32,34,37,40,49,52]], axis=0)
self.crossIndex = np.append(self.crossIndex, [[4,5,12,13,19,22,31,34,37,39,40,41,43,49]], axis=0)
self.crossIndex = np.append(self.crossIndex, [[3,4,13,14,22,25,28,31,40,46,48,49,50,52]], axis=0)

print(cross)

#  WHITE:0 - U
# YELLOW:1 - D
#  GREEN:2 - L
#   BLUE:3 - R
# ORANGE:4 - B
#    RED:5 - F