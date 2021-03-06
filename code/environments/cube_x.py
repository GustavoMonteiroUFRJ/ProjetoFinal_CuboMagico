#----------------------------------------------------------------------
# Matplotlib Rubik's cube simulator
# Written by Jake Vanderplas
# Adapted from cube code written by David Hogg
#   https://github.com/davidwhogg/MagicCube

import numpy as np
#matplotlib.use("TkAgg")

import matplotlib.pyplot as plt
from matplotlib import widgets
from projection import Quaternion, project_points
from random import choice


import random

import sys
import time

sys.path.append('../solvers/cube3/')
from solver_algs import Kociemba

import argparse

#from solver_algs import Korf
#from solver_algs import Optimal


class Cube_x:

    def tf_dtype(self):
        import tensorflow as tf
        return(tf.uint8)

    def __init__(self,N=3,moveType=None):
        self.dtype = np.uint8
        
        self.N = N

        self.legalPlays_qtm = [[f,n] for f in ['U','D','L','R','B','F'] for n in [-1,1]]
        self.legalPlays_qtm_rev = [[f,n] for f in ['U','D','L','R','B','F'] for n in [1,-1]]
        self.legalPlays = list(self.legalPlays_qtm)
        self.legalPlays_rev = list(self.legalPlays_qtm_rev)

        if moveType == "htm" or moveType == "htmaba": # GUSTAVO: Define movimentos duplos como 1 movimento 
            [self.legalPlays.append(2*[[x,1]]) for x in ['U','D','L','R','B','F']] 
            [self.legalPlays_rev.append(2*[[x,1]]) for x in ['U','D','L','R','B','F']]
        if moveType == "htmaba":
            for x in ['U','D','L','R','B','F']:
                for n in [1,-1]:
                    for y in ['U','D','L','R','B','F']:
                        if x == y:
                            continue
                        for n2 in [1,-1]:
                            move = [[x,n],[y,n2],[x,-n]]
                            move_rev = [[x,n],[y,-n2],[x,-n]]

                            self.legalPlays.append(move)
                            self.legalPlays_rev.append(move_rev)


        ### Solved cube
        self.solvedState = np.array([],dtype=int)
        for i in range(6):
            self.solvedState = np.concatenate((self.solvedState,np.arange(i*(N**2),(i+1)*(N**2)))) # GUSTAVO: Array de 0 a 53


        ## Seguindo a nomeclatura do http://www.cubovelocidade.com.br/tutoriais/cubo-magico-blindfolded.html
        
        self.corner_index = np.array([[0,47,26]], dtype=int)
        self.corner_index = np.append(self.corner_index, [[6,29,53]], axis=0)
        self.corner_index = np.append(self.corner_index, [[8,38,35]], axis=0)
        self.corner_index = np.append(self.corner_index, [[2,20,44]], axis=0)
        self.corner_index = np.append(self.corner_index, [[11,24,45]], axis=0)
        self.corner_index = np.append(self.corner_index, [[17,51,27]], axis=0)
        self.corner_index = np.append(self.corner_index, [[15,33,36]], axis=0)
        self.corner_index = np.append(self.corner_index, [[9,42,18]], axis=0)    
        
        self.edge_index = np.array([[3,50]], dtype=int) #A 0
        self.edge_index = np.append(self.edge_index, [[1,23]], axis=0) #B 1
        self.edge_index = np.append(self.edge_index, [[5,41]], axis=0) #C 2
        self.edge_index = np.append(self.edge_index, [[7,32]], axis=0) #D 3
        self.edge_index = np.append(self.edge_index, [[25,46]], axis=0) #E 4
        self.edge_index = np.append(self.edge_index, [[19,43]], axis=0) #F 5
        self.edge_index = np.append(self.edge_index, [[34,37]], axis=0) #G 6
        self.edge_index = np.append(self.edge_index, [[28,52]], axis=0) #L 7
        self.edge_index = np.append(self.edge_index, [[14,48]], axis=0) #M 8
        self.edge_index = np.append(self.edge_index, [[10,21]], axis=0) #N 9
        self.edge_index = np.append(self.edge_index, [[12,39]], axis=0) #P 10
        self.edge_index = np.append(self.edge_index, [[16,30]], axis=0) #R 11


        self.crossIndex = np.array([[1,3,4,5,7,13,22,23,31,32,40,41,49,50]], dtype=int)  # wite cross index
        self.crossIndex = np.append(self.crossIndex, [[4,10,12,13,14,16,21,22,30,31,39,40,48,49]], axis=0) # yellow cross index
        self.crossIndex = np.append(self.crossIndex, [[1,4,10,13,19,21,22,23,25,31,40,43,46,49]], axis=0) # green cross index
        self.crossIndex = np.append(self.crossIndex, [[4,7,13,16,22,28,30,31,32,34,37,40,49,52]], axis=0) # blue  cross index
        self.crossIndex = np.append(self.crossIndex, [[4,5,12,13,19,22,31,34,37,39,40,41,43,49]], axis=0) # orange cross index
        self.crossIndex = np.append(self.crossIndex, [[3,4,13,14,22,25,28,31,40,46,48,49,50,52]], axis=0) # red cross index   

        self.sample_group = dict()
        self.sample_group['gift_box'] = np.array([15,1,17,3,4,5,9,7,11, 6,10,8,12,13,14,0,16,2, 53,52,51,21,22,23,38,37,36, 44,43,42,30,31,32,47,46,45, 26,25,24,39,40,41,29,28,27, 35,34,33,48,49,50,20,19,18], dtype=int)
        self.sample_group['cube_in_the_cube'] = np.array([51,48,45,3,4,46,6,7,47, 9,10,36,12,13,37,44,41,38, 18,19,11,21,22,14,15,16,17, 8,28,29,5,31,32,2,1,0, 20,23,26,39,40,25,42,43,24, 33,30,27,34,49,50,35,52,53], dtype=int)
        self.sample_group['displaced_motif'] = np.array([15,12,9,3,4,10,6,7,11, 2,5,8,1,13,14,0,16,17, 44,19,42,41,22,39,38,37,36, 27,28,29,30,31,32,47,46,45, 26,25,24,23,40,21,20,43,18, 35,34,33,48,49,50,51,52,53], dtype=int)
        self.sample_group['six_spots'] = np.array([51,48,45,52,4,46,53,50,47, 42,39,36,43,13,37,44,41,38, 9,10,11,12,22,14,15,16,17, 8,7,6,5,31,3,2,1,0, 20,23,26,19,40,25,18,21,24, 33,30,27,34,49,28,35,32,29], dtype=int)
        self.sample_group['order_in_chaos'] = np.array([35,1,33,52,4,46,6,50,27, 9,39,20,43,13,14,24,41,26, 18,10,36,12,22,23,44,16,38, 47,7,29,5,31,3,45,34,51, 11,37,17,19,40,25,42,21,15, 2,30,8,48,49,28,0,32,53], dtype=int)
        
        
        
        ### Colors to nnet representation
        # TODO only works for 3x3x3
        #  WHITE:0 - U
        # YELLOW:1 - D
        #  GREEN:2 - L
        #   BLUE:3 - R
        # ORANGE:4 - B
        #    RED:5 - F
        self.colorsToGet = []
        self.colorsToNnetRep = np.zeros((6*(N**2),1),dtype=np.uint8)
        idx = 0
        edgePos = 0
        cornerPos = 0
        for face in range(6):
            for i in range(N):
                for j in range(N):
                    ### Encoding of colors to get based on index
                    if i == 1 and j == 1: # center piece
                        self.colorsToNnetRep[idx,0] = 0
                    elif i == 1 or j == 1: # edge piece
                        self.colorsToNnetRep[idx,0] = edgePos
                        edgePos = edgePos + 1
                    else: # corner piece
                        self.colorsToNnetRep[idx,0] = cornerPos
                        cornerPos = cornerPos + 1

                    ### Colors to get
                    if face == 0 or face == 1:
                        if i != 1 or j != 1:
                            self.colorsToGet.append(idx)
                    elif face == 4 or face == 5:
                        if i != 1 and j == 1:
                            self.colorsToGet.append(idx)

                    
                    idx = idx + 1

        self.colorsToGet = np.sort(self.colorsToGet)

        ### Pre-compute rotation idxs
        self.rotateIdxs_old = dict()
        self.rotateIdxs_new = dict()
        for f,n in self.legalPlays_qtm:
            move = "_".join([f,str(n)])

            self.rotateIdxs_new[move] = np.array([],dtype=int)
            self.rotateIdxs_old[move] = np.array([],dtype=int)

            colors = np.zeros((6,N,N),dtype=np.int64)
            colors_new = np.copy(colors)

            # WHITE:0, YELLOW:1, BLUE:2, GREEN:3, ORANGE: 4, RED: 5
            adjFaces = {0:np.array([2,5,3,4]),
                        1:np.array([2,4,3,5]),
                        2:np.array([0,4,1,5]),
                        3:np.array([0,5,1,4]),
                        4:np.array([0,3,1,2]),
                        5:np.array([0,2,1,3])
                        }
            adjIdxs = {0:{2:[range(0,N),N-1],3:[range(0,N),N-1],4:[range(0,N),N-1],5:[range(0,N),N-1]},
                       1:{2:[range(0,N),0],3:[range(0,N),0],4:[range(0,N),0],5:[range(0,N),0]},
                       2:{0:[0,range(0,N)],1:[0,range(0,N)],4:[N-1,range(N-1,-1,-1)],5:[0,range(0,N)]},
                       3:{0:[N-1,range(0,N)],1:[N-1,range(0,N)],4:[0,range(N-1,-1,-1)],5:[N-1,range(0,N)]},
                       4:{0:[range(0,N),N-1],1:[range(N-1,-1,-1),0],2:[0,range(0,N)],3:[N-1,range(N-1,-1,-1)]},
                       5:{0:[range(0,N),0],1:[range(N-1,-1,-1),N-1],2:[N-1,range(0,N)],3:[0,range(N-1,-1,-1)]}
                       }
            faceDict = {'U':0,'D':1,'L':2,'R':3,'B':4,'F':5}
            face = faceDict[f]

            sign = 1
            if n < 0:
                sign = -1

            facesTo = adjFaces[face]
            if sign == 1:
                facesFrom = facesTo[(np.arange(0,len(facesTo))+1) % len(facesTo)]
            elif sign == -1:
                facesFrom = facesTo[(np.arange(len(facesTo)-1,len(facesTo)-1+len(facesTo))) % len(facesTo)]

            ### Rotate face TODO only works for 3x3x3
            cubesIdxs = [[0,range(0,N)],[range(0,N),N-1],[N-1,range(N-1,-1,-1)],[range(N-1,-1,-1),0]]
            cubesTo = np.array([0,1,2,3])
            if sign == 1:
                cubesFrom = cubesTo[(np.arange(len(cubesTo)-1,len(cubesTo)-1+len(cubesTo))) % len(cubesTo)]
            elif sign == -1:
                cubesFrom = cubesTo[(np.arange(0,len(cubesTo))+1) % len(cubesTo)]

            for i in range(4):
                idxsNew = [[idx1,idx2] for idx1 in np.array([cubesIdxs[cubesTo[i]][0]]).flatten() for idx2 in np.array([cubesIdxs[cubesTo[i]][1]]).flatten()]
                idxsOld = [[idx1,idx2] for idx1 in np.array([cubesIdxs[cubesFrom[i]][0]]).flatten() for idx2 in np.array([cubesIdxs[cubesFrom[i]][1]]).flatten()]
                for idxNew,idxOld in zip(idxsNew,idxsOld):
                    flatIdx_new = np.ravel_multi_index((face,idxNew[0],idxNew[1]),colors_new.shape)
                    flatIdx_old = np.ravel_multi_index((face,idxOld[0],idxOld[1]),colors.shape)
                    self.rotateIdxs_new[move] = np.concatenate((self.rotateIdxs_new[move],[flatIdx_new]))
                    self.rotateIdxs_old[move] = np.concatenate((self.rotateIdxs_old[move],[flatIdx_old]))
                #colors_new[face][cubesIdxs[cubesTo[i]]] = colors[face][cubesIdxs[cubesFrom[i]]]

            ### Rotate adjacent faces
            faceIdxs = adjIdxs[face]
            for i in range(0,len(facesTo)):
                faceTo = facesTo[i]
                faceFrom = facesFrom[i]
                idxsNew = [[idx1,idx2] for idx1 in np.array([faceIdxs[faceTo][0]]).flatten() for idx2 in np.array([faceIdxs[faceTo][1]]).flatten()]
                idxsOld = [[idx1,idx2] for idx1 in np.array([faceIdxs[faceFrom][0]]).flatten() for idx2 in np.array([faceIdxs[faceFrom][1]]).flatten()]
                for idxNew,idxOld in zip(idxsNew,idxsOld):
                    flatIdx_new = np.ravel_multi_index((faceTo,idxNew[0],idxNew[1]),colors_new.shape)
                    flatIdx_old = np.ravel_multi_index((faceFrom,idxOld[0],idxOld[1]),colors.shape)
                    self.rotateIdxs_new[move] = np.concatenate((self.rotateIdxs_new[move],[flatIdx_new]))
                    self.rotateIdxs_old[move] = np.concatenate((self.rotateIdxs_old[move],[flatIdx_old]))

                #colors_new[faceTo][faceIdxs[faceTo]] = colors[faceFrom][faceIdxs[faceFrom]]

        ### Precompute transpose
        def rotateFace(colors_cube,face,sign,N):
            colors_cube_new = np.copy(colors_cube)

            cubesIdxs = [[0,range(0,N)],[range(0,N),N-1],[N-1,range(N-1,-1,-1)],[range(N-1,-1,-1),0]]
            cubesTo = np.array([0,1,2,3])
            if sign == 1:
                cubesFrom = cubesTo[(np.arange(len(cubesTo)-1,len(cubesTo)-1+len(cubesTo))) % len(cubesTo)]
            elif sign == -1:
                cubesFrom = cubesTo[(np.arange(0,len(cubesTo))+1) % len(cubesTo)]

            for i in range(4):
                colors_cube_new[face][cubesIdxs[cubesTo[i]]] = colors_cube[face][cubesIdxs[cubesFrom[i]]]

            return(colors_cube_new)

        # (topo)WHITE:0, YELLOW:1, GREEN:2 , BLUE:3(direita), ORANGE: 4, RED: 5(frente)
        self.colorOrdIdxs = dict()
        self.faceSwapIdxs = dict()
        for faceTranspose in [0,2,4,-1]:
            idxsNew = []
            if faceTranspose == 0:
                newFaceOrder = [0,1,4,5,3,2]
                rotateFaces = [0,1]
                rotateDirs = [-1,1]
            elif faceTranspose == 2:
                newFaceOrder = [5,4,2,3,0,1]
                rotateFaces = [2,3,4,4,1,1]
                rotateDirs = [-1,1,1,1,1,1]
            elif faceTranspose == 4:
                newFaceOrder = [2,3,1,0,4,5]
                rotateFaces = [4,5,0,1,2,3]
                rotateDirs = [-1,1,1,1,1,1]
            elif faceTranspose == -1:
                newFaceOrder = [0,1,3,2,4,5]
                rotateFaces = []
                rotateDirs = []

            ### Swap colors
            for face in newFaceOrder:
                for i in range(N):
                    for j in range(N):
                        idx = np.ravel_multi_index((face,i,j),(6,3,3))
                        idxsNew.append(idx)
            idxsNew = np.array(idxsNew)

            idxsNew = idxsNew.reshape([6,N,N])
            for rotateF,rotateD in zip(rotateFaces,rotateDirs):
                idxsNew = rotateFace(idxsNew,rotateF,rotateD,N)

            if faceTranspose == -1:
                idxsNew_tmp = idxsNew.copy()
                for face in range(6):
                    idxsNew[face,0,:] = idxsNew_tmp[face,2,:]
                    idxsNew[face,2,:] = idxsNew_tmp[face,0,:]
                    
            self.colorOrdIdxs[faceTranspose] = idxsNew.flatten()
            
            ### Swap faces
            swappedColors_cube = self.solvedState.reshape([6,N,N])

            swappedColorsFaces_cube = np.zeros([6,N,N],dtype=int)
            for idx,face in enumerate(newFaceOrder):
                swappedColorsFaces_cube[idx] = swappedColors_cube[face]

            for rotateF,rotateD in zip(rotateFaces,rotateDirs):
                swappedColorsFaces_cube = rotateFace(swappedColorsFaces_cube,rotateF,rotateD,N)

            if faceTranspose == -1:
                swappedColorsFaces_cube_tmp = swappedColorsFaces_cube.copy()
                for face in range(6):
                    swappedColorsFaces_cube[face,0,:] = swappedColorsFaces_cube_tmp[face,2,:]
                    swappedColorsFaces_cube[face,2,:] = swappedColorsFaces_cube_tmp[face,0,:]

            self.faceSwapIdxs[faceTranspose] = swappedColorsFaces_cube.flatten()

    def next_state(self,colors, move, layer=0):
        """Rotate Face"""
        colorsNew = colors.copy()

        if type(move[0]) == type(list()):
            for move_sub in move:
                colorsNew = self.next_state(colorsNew,move_sub)
        else:
            moveStr = "_".join([move[0],str(move[1])])

            if len(colors.shape) == 1:
                colorsNew[self.rotateIdxs_new[moveStr]] = colors[self.rotateIdxs_old[moveStr]].copy()
            else:
                colorsNew[:,self.rotateIdxs_new[moveStr]] = colors[:,self.rotateIdxs_old[moveStr]].copy()

        return(colorsNew)

    def state_to_nnet_input(self,colors,randTransp=False):
        #colorsSort = self.get_transposes_color_sort(colors)
        #representation = self.get_nnet_representation(colorsSort)

        colors = colors.astype(self.dtype)
        if len(colors.shape) == 1:
            colors = np.expand_dims(colors,0)
        """
        if randTransp:
            colorsSort = self.get_transposes_color_sort(colors,selectRand=True)
            transpIdx = np.random.randint(colorsSort.shape[1])
            representation = self.get_nnet_representation(colorsSort[:,transpIdx,:])
        else:
            colors = np.argsort(colors,axis=1)
            colors = colors[:,self.colorsToGet]
            
            representation = self.get_nnet_representation(colors)
        """
        
        representation = self.get_nnet_representation(colors)
        return(representation)

    def get_nnet_representation(self,colors):
        colors = colors.astype(self.dtype)
        
        representation = colors/(self.N**2)
        representation = representation.astype(self.dtype)

        #representation = self.colorsToNnetRep[colors]
        #newShape = list(representation.shape[0:-2]) + [representation.shape[-2]*representation.shape[-1]]
        #representation = np.reshape(representation,newShape)

        return(representation)

    def get_transposes_color_sort(self,colors,selectRand=False,colorSort=True):
        colors = colors.astype(np.int8)
        if len(colors.shape) == 1:
            colors = np.expand_dims(colors,0)
        colorsTop0 = np.argsort(colors,axis=1).astype(np.int8) # convert to cube index
        colorsTop5 = self.transpose(colorsTop0,2)
        colorsTop1 = self.transpose(colorsTop5,2)
        colorsTop4 = self.transpose(colorsTop1,2)
        colorsTop2 = self.transpose(colorsTop0,4)
        colorsTop3 = self.transpose(self.transpose(colorsTop2,4),4)

        colorsTopAll = [colorsTop0,colorsTop1,colorsTop2,colorsTop3,colorsTop4,colorsTop5]
        if selectRand == True:
            colorsTopAll = [random.choice(colorsTopAll)]

        colorsList = []
        for colors in colorsTopAll:
            colors_posIndex = np.argsort(colors,axis=1).astype(np.int8)

            colors2 = self.transpose(colors_posIndex,0,indexType="position")
            colors2_posIndex = np.argsort(colors2,axis=1).astype(np.int8)
            
            colors3 = self.transpose(colors2_posIndex,0,indexType="position")
            colors3_posIndex = np.argsort(colors3,axis=1).astype(np.int8)
            
            colors4 = self.transpose(colors3_posIndex,0,indexType="position")
        
            colors_refl = self.transpose(colors_posIndex,-1,indexType="position")
            colors2_refl = self.transpose(colors2_posIndex,-1,indexType="position")
            colors3_refl = self.transpose(colors3_posIndex,-1,indexType="position")
            colors4_refl = self.transpose(colors4,-1)
            
            colorsList.extend([colors,colors2,colors3,colors4,colors_refl,colors2_refl,colors3_refl,colors4_refl])

        transposeList = []
        if colorSort:
            for colors in colorsList:
                colorsSort = colors
                colorsSort = colorsSort[:,self.colorsToGet]
                transposeList.append(colorsSort)
        else:
            for colors in colorsList:
                colors = np.argsort(colors,axis=1).astype(np.int8)
                transposeList.append(colors)


        allTransps = np.stack(transposeList,axis=1)
        cubesRet = allTransps

        #matchIdxs = np.argmax(allTransps[:,:,1] == 0,axis=1)
        #cubesRet = [allTransps[i,matchIdxs[i],:] for i in range(allTransps.shape[0])]
        #cubesRet = np.expand_dims(np.stack(cubesRet,0),1)
        return(cubesRet)

    def getReward(self,colors,isSolved=None):
        reward = np.ones(shape=(colors.shape[0]))
        return(reward)

    def transpose(self,colors,faceTranspose,indexType="cube"):
        colors = colors.astype(np.int8)
        if len(colors.shape) == 1:
            colors = np.expand_dims(colors,0)

        ### Swap faces
        if indexType == "cube":
            # Convert to position index
            colors = np.argsort(colors,axis=1).astype(np.int8)
        swappedFaces = colors[:,self.faceSwapIdxs[faceTranspose]]

        ### Swap colors
        colorsArgSort = np.argsort(swappedFaces,axis=1).astype(np.int8) # convert to cube index
        colorsArgSortSelect = colorsArgSort[:,self.colorOrdIdxs[faceTranspose]]
        colorsNew = colorsArgSortSelect

        return(colorsNew)

    
    def get_random_state(self):
        # Gera cubos embaralhados com a cruz de baixo feita. 
        # TODO fazer para qualquer cruz.
        
        #### PERMITATION
        # desired cross patter 
        cross_edge_position = []
        cross_corner_position = []

        # scrambling
        corner_position_mix = np.random.choice( np.arange(len(self.corner_index)), len(self.corner_index), replace=False)
        edge_position_mix = np.random.choice( np.arange(len(self.edge_index)), len(self.edge_index), replace=False)

        def pattern(scramble, pattern):
            scramble_c = scramble.copy()
            for peca in pattern:
                origem = list(scramble_c).index(peca)
                scramble_c[[peca, origem]] = scramble_c[[origem, peca]]
            return scramble_c

        # Flip pices for match the desired patter.
        corner_position_mix_pattern = pattern(corner_position_mix, cross_corner_position)
        edge_position_mix_pattern = pattern(edge_position_mix, cross_edge_position)

        def parity(scramble):
            nao_visitado = np.array([True]*len(scramble), dtype=bool)
            parity = False
            for i in range(len(scramble)):
                tam_ciclo = 0
                if nao_visitado[i]:
                    nao_visitado[i] = False
                    destino = scramble[i]
                    tam_ciclo = 1
                    while nao_visitado[destino]:
                        nao_visitado[destino] = False
                        destino = scramble[destino]
                        tam_ciclo = tam_ciclo + 1

                    if tam_ciclo%2 == 0:
                        parity = np.logical_xor(True,parity)
            return parity

        # Checking if there is edges parity and corner parity, if ther is only one, de scrambling is unresolvable
        check_parity_corner = parity(corner_position_mix_pattern)
        check_parity_edges = parity(edge_position_mix_pattern)
        
        # flip 2 pices if only one parity is detected.
        if np.logical_xor(check_parity_corner, check_parity_edges):
            edge_out_pattern = list(set(edge_position_mix_pattern) - set(cross_edge_position))
            if len(edge_out_pattern) >= 2:
                edge_to_chenge = np.random.choice( edge_out_pattern, 2, replace=False)
                edge_position_mix_pattern[edge_to_chenge] = edge_position_mix_pattern[np.flip(edge_to_chenge)] 
            else:
                corner_out_pattern = list(set(corner_position_mix_pattern) - set(cross_corner_position))
                if len(corner_out_pattern) >= 2:
                    corner_to_chenge = np.random.choice( corner_out_pattern, 2, replace=False)
                    corner_position_mix_pattern[corner_to_chenge] = corner_position_mix_pattern[np.flip(corner_to_chenge)]
                else:
                    print("Algo muito errado aconteceu, provavelmente o proprio padrao desejaval nao seja resolvivel.")

        #### ORIENTATION
        # desired cross patter 
        # cross_edge_position = []
        cross_edge_position = []
        cross_corner_position = []

        # 
        edge_orientetion_mix = np.random.choice( [0,1], len(self.edge_index))
        corner_orientetion_mix =  np.random.choice( [0,1,2], len(self.corner_index))        
        
        edge_orientetion_mix[cross_edge_position] = 0
        corner_orientetion_mix[cross_corner_position] = 0
        
        def fix_orientetion(scramble, modulo, patter):
            index = np.arange(len(scramble))
            pice = np.random.choice(np.delete(index, patter))
            index_out = np.delete(index,pice)
            scramble[pice] = (modulo - sum(scramble[index_out]) % modulo ) % modulo

        fix_orientetion(edge_orientetion_mix, 2, cross_edge_position)
        fix_orientetion(corner_orientetion_mix, 3, cross_corner_position)

        def build(corner_position, edge_position, corner_orientetion, edge_orientation):
            cubo = self.solvedState.copy() # Apenas para pegar o shape e os centros.
            c_orientetions = np.array([[0,1,2],[2,0,1],[1,2,0]])
            e_orientetions = np.array([[0,1],[1,0]])

            for corner_i in range(len(self.corner_index)):
                coner_stickers_index = self.corner_index[corner_i]
                cubo[coner_stickers_index] = self.corner_index[corner_position[corner_i]]
                cubo[coner_stickers_index] = cubo[coner_stickers_index][c_orientetions[corner_orientetion[corner_i]]]

            for edge_i in range(len(self.edge_index)):
                edge_stickers_index = self.edge_index[edge_i]
                cubo[edge_stickers_index] = self.edge_index[edge_position[edge_i]]
                cubo[edge_stickers_index] = cubo[edge_stickers_index][e_orientetions[edge_orientation[edge_i]]]
                    
            return cubo 

        # print(corner_position_mix_pattern)
        # print(edge_position_mix_pattern)
        # print(corner_orientetion_mix)
        # print(edge_orientetion_mix)

        return build(corner_position_mix_pattern, edge_position_mix_pattern, corner_orientetion_mix, edge_orientetion_mix)
    
    # Passa da representação possição orientação para cores
    def build(self, corner_position, edge_position, corner_orientetion, edge_orientation):
        cubo = self.solvedState.copy() # Apenas para pegar o shape e os centros.

        corner_position = np.array(corner_position, dtype=np.int)
        edge_position = np.array(edge_position, dtype=np.int)
        corner_orientetion = np.array(corner_orientetion, dtype=np.int)
        edge_orientation = np.array(edge_orientation, dtype=np.int)


        c_orientetions = np.array([[0,1,2],[2,0,1],[1,2,0]])
        e_orientetions = np.array([[0,1],[1,0]])

        for corner_i in range(len(self.corner_index)):
            coner_stickers_index = self.corner_index[corner_i]
            cubo[coner_stickers_index] = self.corner_index[corner_position[corner_i]]
            cubo[coner_stickers_index] = cubo[coner_stickers_index][c_orientetions[corner_orientetion[corner_i]]]

        for edge_i in range(len(self.edge_index)):
            edge_stickers_index = self.edge_index[edge_i]
            cubo[edge_stickers_index] = self.edge_index[edge_position[edge_i]]
            cubo[edge_stickers_index] = cubo[edge_stickers_index][e_orientetions[edge_orientation[edge_i]]]
                
        return cubo
    
    # Passa da representação por cores para possição orientação 
    def modelo_permutacao_orientacao(colors):
        corner_position = []
        edge_position = []
        corner_orientetion = []
        edge_orientation = []
        
        for i in range(len(self.corner_index)):
            sticker = colors[self.corner_index[i][0]]
            posicion = int(list({ i for i in range(len(self.corner_index)) if sticker in self.corner_index[i]})[0])
            corner_position = np.append(corner_position, posicion)
        corner_position = np.array(corner_position, dtype=np.int)
        
        for i in range(len(self.edge_index)):
            sticker = colors[self.edge_index[i][0]]
            posicion = int(list({ i for i in range(len(self.edge_index)) if sticker in self.edge_index[i]})[0])
            edge_position = np.append(edge_position, posicion)
        edge_position = np.array(edge_position, dtype=np.int)
            
        for i in range(len(self.corner_index)):
            piece = colors[[self.corner_index[i]]]
            orientetion = np.where(piece == self.corner_index[corner_position[i]][0])
            corner_orientetion = np.append(corner_orientetion, orientetion)
        corner_orientetion = np.array(corner_orientetion, dtype=np.int)
            
        for i in range(len(self.edge_index)):
            piece = colors[[self.edge_index[i]]]
            orientetion = np.where(piece == self.edge_index[edge_position[i]][0])
            edge_orientation = np.append(edge_orientation, orientetion)
        edge_orientation = np.array(edge_orientation, dtype=np.int)
        
        return corner_position, edge_position, corner_orientetion, edge_orientation

    # retorna uma lista de numCubes cubos embaralhados com ate scrambleRange movimentos.
    def generate_envs(self,numCubes,scrambleRange,probs=None,returnMoves=False):
        assert(scrambleRange[0] >= 0)
        scrambs = range(scrambleRange[0],scrambleRange[1]+1)
        legal = self.legalPlays_qtm
        cubes = []

        scrambleNums = np.zeros([numCubes],dtype=int)
        moves_all = []
        for cubeNum in range(numCubes):
            scrambled = self.get_solved_state()

            # Get scramble Num
            scrambleNum = np.random.choice(scrambs,p=probs)
            scrambleNums[cubeNum] = scrambleNum
            # Scramble cube
            moves = []
            for i in range(scrambleNum):
                move = choice(legal)
                scrambled = self.next_state(scrambled, move)
                moves.append(move)

            cubes.append(scrambled)
            moves_all.append(moves)

        if returnMoves:
            return(cubes,scrambleNums,moves_all)
        else:
            return(cubes,scrambleNums)


