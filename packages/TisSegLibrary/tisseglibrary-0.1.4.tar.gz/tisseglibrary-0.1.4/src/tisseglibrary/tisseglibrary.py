from mimetypes import init
import SimpleITK as sitk
import numpy as np
from skimage import exposure, morphology, util
from sklearn.cluster import KMeans
import scipy as sp
import slicer
from operator import xor

version = 'v0.3.1'

def geo_strep(marker, mask, se, method):
        if method == 'dilate':
            result = np.bitwise_and(morphology.binary_dilation (marker, se), mask).astype(np.int32)
        elif method == 'erode':
            result = np.bitwise_or(morphology.binary_erosion(marker, se), mask).astype(np.int32)
        else:
            pass
        return result  
def basic_reconstruction(marker, mask, se, method):
    prev_marker = marker
    new_marker = geo_strep(prev_marker, mask, se, method)
    while np.sum(prev_marker - new_marker)!=0:
        prev_marker = new_marker
        new_marker = geo_strep(prev_marker, mask, se, method)
    result=new_marker
    return result
def open_reconstruction(image, se, n):
    for i in range (n) :
        result_erosion = morphology.binary_erosion (image, se).astype(np.int32)
        image = result_erosion
    marker = result_erosion
    result=basic_reconstruction(marker, image, se, 'dilate')
    return result
def close_reconstruction(image, se, n):
    for i in range (n) :
        result_erosion = morphology.binary_dilation (image, se).astype(np.int32)
        image = result_erosion
    marker = result_erosion
    result=basic_reconstruction(marker, image, se, 'erode')
    return result    

def cluster(I_primary, ncluster, numberOfPartitions, RangeSlice, primerosSlices, ultimosSlices, I_optional = None, 
             mask = None, centroids = None):

        '''
        Aplica una clusterización tipo K-Means, utilizando una o dos imágenes. Existe la posibilidad de realizar el proceso solo
        en las zonas de la imagen indicadas en la máscara. En caso de que se proporcionen centroides, estos se utilizan como centroides
        iniciales en la clusterización. 
        La clusterización se realiza en grupos de cortes, el tamaño de los mismos se indica con la variable numberOfPartitions. Pero 
        en caso de que se estén analizando los extremos de la imagen, estos grupos tienen siempre tamaño 1.

        Inputs:
            Iprimary -- imagen a clusterizar
            ncluster -- número de cluster
            numberOfPartitions -- tamaño de los grupos de cortes 
            RangeSlices --  rango de cortes de la imagen que se desea segmentar
            primerosSlices -- corte en el que se acaba el extremo inferior de la imagen
            ultimosSlices-- corte en el que empeiza el extremo superior de la imagen
            I_optional -- imagen opcional a clusterizar
            mask -- máscara con la zona de la imagen/imagenes que se quiere analizar
            centroids -- centroides que se utilizan en la inicializacion del K-Means

        Outputs:
            classImage -- label map de salida de la clusterización 
            mean_classes -- matriz con el número de clusters y la media de cada una de ellas

        '''
        I_primary_mat = sitk.GetArrayFromImage(I_primary)

        if mask==None:
            mask_mat = np.ones(I_primary_mat.shape)
        else:
            mask_mat = sitk.GetArrayFromImage(mask)
        
        I_primary_mat_mask = I_primary_mat [mask_mat == 1]
        
        if I_optional==None:
            I = I_primary_mat_mask .reshape(-1, 1)
            mask = mask_mat[mask_mat ==1].reshape(-1, 1)
        else:
            #Paso dados a forma Nx2
            #En caso de tener dos imagenes se utilizan ambas para hacer la clusterizacion
            I_optional_mat = sitk.GetArrayFromImage(I_optional)
            I_optional_mat_mask = I_optional_mat [mask_mat == 1]
            I_concatenate = np.concatenate ((I_optional_mat_mask, I_primary_mat_mask))
            I = I_concatenate.reshape(2, I_primary_mat_mask.shape[0]).T 
            mask_concatenate = np.concatenate ((mask_mat[mask_mat ==1], mask_mat[mask_mat ==1]))
            mask = mask_concatenate

        if centroids is None:
            centroids  = np.array([[0,0], [255,0], [0,255]])

        #K-means
        aux =0
        classes = np.zeros(I_primary_mat_mask.shape)
        classes =np.squeeze(classes.reshape((-1, 1)))
        
        for i in range (1, (I_primary_mat.shape[0]//numberOfPartitions)+1) : 
            #Si nos encontramos en los extremos del volumen, el número de particiones que se analizan cada vez es igual a uno. 
            if (RangeSlice[0] + ((i-1)*numberOfPartitions)) <= primerosSlices or  (RangeSlice[0] + ((i)*numberOfPartitions)) >= ultimosSlices \
                and  numberOfPartitions>1:

                newnumberOfPartitions = 1
                diferencia = numberOfPartitions - newnumberOfPartitions
                for j in range (1, diferencia+2):
                    kmeans_results = KMeans(ncluster , init= centroids , max_iter = 100) 
                    kmeans_results.fit(I[aux:(aux +((I.shape[0])//(I_primary_mat.shape[0]//numberOfPartitions))//(diferencia+1)), :]) 
                    centroids = kmeans_results.cluster_centers_
                    labels = kmeans_results.predict(I[aux:(aux +((I.shape[0])//(I_primary_mat.shape[0]//numberOfPartitions))//(diferencia+1)), :])
                    classes[aux : (aux +((I.shape[0])//(I_primary_mat.shape[0]//numberOfPartitions))//(diferencia+1))] = labels
                    aux=(aux +((I.shape[0])//(I_primary_mat.shape[0]//numberOfPartitions))//(diferencia+1))
            else:
                #En caso de no estar en los extremos se analizan grupo de slices. Esto grupos tienen el tamaño que indica el usuario en numero de particiones
                kmeans_results = KMeans(ncluster , init= centroids , max_iter = 100) 
                kmeans_results.fit(I[aux:aux+(I.shape[0])//(I_primary_mat.shape[0]//numberOfPartitions), :]) 
                centroids = kmeans_results.cluster_centers_
                labels = kmeans_results.predict(I[aux: aux + (I.shape[0])//(I_primary_mat.shape[0]//numberOfPartitions), :])
                classes[aux : aux + (I.shape[0])//(I_primary_mat.shape[0]//numberOfPartitions)] = labels
                aux=aux + (I.shape[0])//(I_primary_mat.shape[0]//numberOfPartitions) 

        #hallo la media de cada cluster
        Icluster = np.zeros(I_primary_mat.shape)
        Icluster[mask_mat == 1] = classes
        mean_classes= np.zeros((ncluster, 2))

        for k in range (ncluster):
            aux=I_primary_mat[Icluster==k]
            mean_classes[k,0] = np.mean(aux, axis = 0)
            mean_classes [k,1] = k
        mean_classes.sort(axis=0)
        mean_classes = mean_classes[::-1]

        Icluster_img = sitk.GetImageFromArray(Icluster)
        Icluster_img.CopyInformation(I_primary)

        return Icluster_img, mean_classes
        
def clean_border_thigh(input_mask,image_W, image_F):
        # Ponemos las dos tapas inferior y superior para que los muslos no estén pegados al borde del volumen
        pad_filter = sitk.ConstantPadImageFilter()
        pad_filter.SetPadLowerBound([0,0,1])
        pad_filter.SetPadUpperBound([0,0,1])
        pad_input_mask = pad_filter.Execute(input_mask)

        aux_mask = (image_W==0) & (image_F==0)

        pad_filter.SetConstant = 1
        aux_mask = pad_filter.Execute(aux_mask)
        aux_mask_mat = sitk.GetArrayFromImage(aux_mask)
        #Limpiamos la imagen
        struct_element = np.ones([1,4,1])
        aux_mask_mat = open_reconstruction(aux_mask_mat, struct_element, 1).astype(np.int8)
        aux_img = sitk.GetImageFromArray(aux_mask_mat)
        aux_img.CopyInformation(aux_mask)
        aux_mask = aux_img
        # aux_mask = sitk.BinaryGrindPeak(aux_mask)
        aux_bgp = sitk.BinaryGrindPeak((pad_input_mask!=0) | sitk.Cast (aux_mask, sitk.sitkUInt8)) # Quitamos todo lo que no esté pegado al borde
        non_border_seg = sitk.Mask( pad_input_mask, aux_bgp==0) # Enmascaramos con el inverso
        non_border_seg = non_border_seg[:,:,1:-1]
        # Comprobamos si ha desaparecido, calculando el máximo de la imagen y comparandolo con 0
        full_Q = (np.max(sitk.GetArrayFromImage(non_border_seg))!=0) 

        return non_border_seg, full_Q

def act_cont(Img1, Img2, PropagationScaling,CurvatureScaling , AdvectionScaling, sigma, alpha_, beta_, sliceRange,  a=False):
    '''
        Aplica un contorno activo
        
        Inputs:
            Img1 -- imagen base 
            Img2 -- imagen cuyo contorno se quiere ajustar al de la imagen base
            PropagationScaling -- parámetro del contorno activo para ajustar la propagación
            CurvatureScaling -- parámetro del contorno activo para ajustar la curvatura
            AdvectionScaling -- parámetro del contorno activo para ajustar el campo de advección
            sigma -- parámetro del cálculo de la magnitud de gradiente gaussiana
            alpha_, beta_ -- parámetros del filtro sigmeoideo
            sliceRange -- rango de cortes de la imagen que se desea segmentar

        Outputs:
            thes_GAC -- imagen en 3D con el resultado del contorno activo

    '''
    pad_input_mask = 0
    pad_input_mask2 = 0
    initImg = 0
    imgSigmoid = 0
    
    Img1 =sitk.Cast(Img1, sitk.sitkFloat32)
    pad_input_mask_mat  = 0 

    if  sliceRange[1]- sliceRange[0] < 4:
        diferencia = int (4- (sliceRange[1]- sliceRange[0]))
        numeroSlciesAñadir = 1 + diferencia
        #Img2 --> se añade una tapa inferior y tantas tapas superiores como sea necesario para que el número de slices sea de 4 slcies
        Img_aux = Img2[:,:, 0:1]
        Img_aux_mat = sitk.GetArrayFromImage(Img_aux)
        Img2_mat =sitk.GetArrayFromImage(Img2)
        pad_input_mask2_mat=np.insert(Img2_mat, 0, Img_aux_mat, axis=0)
        pad_input_mask2_mat_shape = pad_input_mask2_mat.shape
        Img2_slices_shape = Img2.GetSize()
        Img2_aux = Img2[:,:,int(Img2_slices_shape[2]-1)]
        Img_aux_mat = sitk.GetArrayFromImage(Img_aux)
        posicion=pad_input_mask2_mat_shape[0]
        for i in range (int(diferencia+1)):
            pad_input_mask2_mat=np.insert(pad_input_mask2_mat, posicion, Img_aux_mat, axis=0)
            posicion= pad_input_mask2_mat.shape[0]
        pad_input_mask2 = sitk.GetImageFromArray(pad_input_mask2_mat)

        #Img1  --> en este caso las tapas son el primer y ultimo slice de la imagen.
        Img_aux = Img1[:,:,0:1]
        Img1_mat =sitk.GetArrayFromImage(Img1)
        Img1_aux_mat =sitk.GetArrayFromImage(Img_aux)
        pad_input_mask_mat=np.insert(Img1_mat, 0, Img1_aux_mat, axis=0)
        pad_input_mask_mat_shape = pad_input_mask_mat.shape
        Img1_slices_shape = Img1.GetSize()
        Img1_aux = Img1[:,:,int(Img1_slices_shape[2]-1)]
        Img1_aux_mat=sitk.GetArrayFromImage(Img1_aux)
        posicion=pad_input_mask_mat_shape[0]
        for i in range (int (diferencia+1)):
            pad_input_mask_mat=np.insert(pad_input_mask_mat, posicion, Img1_aux_mat, axis=0)
            posicion= pad_input_mask_mat.shape[0]
        pad_input_mask = sitk.GetImageFromArray(pad_input_mask_mat)

    else:
        #Img1  --> se añade una tapa inferior igual al primer slice y otra superior igual al último
        Img_aux = Img1[:,:,0:1]
        Img1_mat =sitk.GetArrayFromImage(Img1)
        Img1_aux_mat =sitk.GetArrayFromImage(Img_aux)
        pad_input_mask_mat=np.insert(Img1_mat, 0, Img1_aux_mat, axis=0)
        pad_input_mask_mat_shape = pad_input_mask_mat.shape
        Img1_slices_shape = Img1.GetSize()
        Img1_aux = Img1[:,:,int(Img1_slices_shape[2]-1)]
        
        Img1_aux_mat=sitk.GetArrayFromImage(Img1_aux)
        pad_input_mask_mat=np.insert(pad_input_mask_mat, pad_input_mask_mat_shape[0] , Img1_aux_mat, axis=0)
        pad_input_mask = sitk.GetImageFromArray(pad_input_mask_mat)

        #Img2 --> se añade una tapa inferior y otra superior
        Img_aux = Img2[:,:,0:1]
        Img2_mat =sitk.GetArrayFromImage(Img2)
        Img2_aux_mat =sitk.GetArrayFromImage(Img_aux)
        pad_input_mask2_mat=np.insert(Img2_mat, 0, Img2_aux_mat, axis=0)
        pad_input_mask2_mat_shape = pad_input_mask2_mat.shape
        Img2_slices_shape = Img2.GetSize()
        Img2_aux = Img2[:,:,int(Img2_slices_shape[2]-1)]
        
        Img2_aux_mat=sitk.GetArrayFromImage(Img2_aux)
        pad_input_mask2_mat=np.insert(pad_input_mask2_mat, pad_input_mask2_mat_shape[0] , Img2_aux_mat, axis=0)
        pad_input_mask2 = sitk.GetImageFromArray(pad_input_mask2_mat)


    pad_input_mask = sitk.Cast (pad_input_mask, sitk.sitkFloat32)

    #Anisotropic filtering
    timeStep_, conduct, numIter = (0.04, 9.0, 5) 
    curvDiff = sitk.CurvatureAnisotropicDiffusionImageFilter()
    curvDiff.SetTimeStep(timeStep_)
    curvDiff.SetConductanceParameter(conduct)
    curvDiff.SetNumberOfIterations(numIter)
    imgFilter = curvDiff.Execute(pad_input_mask)

    #Magnitude of the gradient
    imgGauss = sitk.GradientMagnitudeRecursiveGaussian(image1=imgFilter, sigma=sigma)

    #Edge potential function
    sigFilt = sitk.SigmoidImageFilter()
    sigFilt.SetAlpha(alpha_)
    sigFilt.SetBeta(beta_)
    sigFilt.SetOutputMaximum(1.0)
    sigFilt.SetOutputMinimum(0.0)
    imgSigmoid = sigFilt.Execute(imgGauss)

    initImg = sitk.Cast(pad_input_mask2,sitk.sitkFloat32) # Cast to float32
    initImg = 0.5-initImg # Condition the image to use it as first inpunt of the filter

    #ActiveContour
    gac = sitk.GeodesicActiveContourLevelSetImageFilter() # Create the active contour filter
    gac.SetPropagationScaling(PropagationScaling) # Set the propagation parameter
    gac.SetCurvatureScaling(CurvatureScaling) # Set the curvature parameter
    gac.SetAdvectionScaling(AdvectionScaling) # Set the advection parameter
    gac.SetMaximumRMSError(0.01) # Set the maximum RMS error of the PDE solution
    gac.SetNumberOfIterations(100) # Set the maximum number of iterations  

    initImg.CopyInformation(pad_input_mask)
    imgSigmoid.CopyInformation(pad_input_mask)

    imgGAC = gac.Execute(initImg, imgSigmoid) # Launch the segmentation
 
    if sliceRange[1]- sliceRange[0] < 4:
        imgGAC= imgGAC[:,:, 0:-int(numeroSlciesAñadir-1)] # Quito los que añado para que haya 4 slices
    imgGAC= imgGAC[:,:,1:-1]
    imgGAC.CopyInformation(Img1)

    #Umbralizacion
    thres_filter = sitk.BinaryThresholdImageFilter()
    thres_filter.SetLowerThreshold(0)
    thres_filter.SetInsideValue(0)
    thres_filter.SetOutsideValue(1)
    thres_GAC= thres_filter.Execute(imgGAC)
    thres_GAC.CopyInformation(Img1)


    return thres_GAC

def CalculateLabelMap(filled_thigh_mask_img, thigh_mask_img , muslo_fat_img_slices,  muslo_water_img_slices, numberOfPartitions, 
                        RangeSlice, primerosSlices, ultimosSlices):
        """
        Crea un label map con la segmentación del muslo

        Inputs:
            filled_thigh_mask_img -- máscara binaria de los muslos
            thigh_mask_img -- máscara binaria de los muslos, con hueso a cero y resto a uno
            muslo_fat_img_slices -- parte de la imagen de grasa que se desea segmentar
            muslo_water_img_slices -- parte de la imagen de agua que se desea segmentar 
            numberOfPartitions-- conjunto de cortes en que se desea hacer la segmenatción
            RangeSlices --  rango de cortes de la imagen que se desea segmentar
            primerosSlices -- corte en el que se acaba el extremo inferior de la imagen
            ultimosSlices-- corte en el que empeiza el extremo superior de la imagen

        Outputs:
            classImage_bw_img -- label map con el resulatdo de la segmentacion 

        """
        
        filled_thigh_mask = sitk.GetArrayFromImage(filled_thigh_mask_img)
        thigh_mask_mat = sitk.GetArrayFromImage(thigh_mask_img)
        muslo_fat_mat = sitk.GetArrayFromImage(muslo_fat_img_slices)
        muslo_water_mat = sitk.GetArrayFromImage (muslo_water_img_slices)

        #Calculo de la médula
        filled_thigh_mask_erode = morphology.erosion (filled_thigh_mask, morphology.ball (2))
        contornomedula = np.multiply(util.invert(thigh_mask_mat), filled_thigh_mask_erode)
        contornomedula_dilate = morphology.dilation(contornomedula, morphology.ball(1))
        marrowAndbone =  sp.ndimage.binary_fill_holes(contornomedula_dilate, structure=np.ones((1,3,2))).astype(np.int32)
        contornomedula_img = sitk.GetImageFromArray(marrowAndbone)
        contornomedula_img.CopyInformation(muslo_fat_img_slices)
        marrow= morphology.opening(np.multiply(marrowAndbone, thigh_mask_mat), morphology.ball(2))
        
        #Calculo del hueso
        marrowAndbone = sp.ndimage.binary_fill_holes(contornomedula_dilate, structure=np.ones((1,3,3))).astype(np.int32)
        marrowAndbone_img = sitk.GetImageFromArray(marrowAndbone)
        marrowAndbone_img.CopyInformation(muslo_fat_img_slices)
        
        marrowAndbone_clean_img= sitk.BinaryOpeningByReconstruction(marrowAndbone_img,kernelRadius=[3,3,3])
        
        marrowAndbone_clean_mat = sitk.GetArrayFromImage(marrowAndbone_clean_img)
        marrow_dilate = morphology.dilation(marrow.astype(np.int32), morphology.ball(7))
        marrow_dilate = morphology.dilation(marrow_dilate.astype(np.int32), morphology.ball(3))

        bone = np.multiply(marrow_dilate , marrowAndbone_clean_mat)
        
        #Calculo de la fracción grasa (FF)
        muslo_fat_eps =np.where(muslo_fat_mat==0, np.finfo(float).eps, muslo_fat_mat)  #Así evitamos el 0/0
        muslo_water_eps =np.where(muslo_water_mat==0, np.finfo(float).eps, muslo_water_mat) 
        FF_mat = np.divide(muslo_fat_eps, (muslo_fat_eps+muslo_water_eps)) 
        FF_mat_clean = np.multiply(FF_mat, filled_thigh_mask)
        FF_img_clean= sitk.GetImageFromArray(FF_mat_clean)
        FF_img_clean.CopyInformation(muslo_fat_img_slices)

        #Cluster --> Kmeans a FF
        numberOfClasses = 3
        [classImage_img,mean_classes]=cluster(FF_img_clean, numberOfClasses, numberOfPartitions, RangeSlice,
                                              primerosSlices, ultimosSlices,  mask = filled_thigh_mask_img, 
                                              centroids = np.array([[0], [1], [0.5]]))

        classImage = sitk.GetArrayFromImage(classImage_img)

        #Grasa
        sat_mat = np.where (classImage == mean_classes[1,1], 1, 0)
        sat_mat = sat_mat.astype(np.float64)
        sat_withoutBone = np.where (bone == 1, 0, sat_mat)
        class11_img= sitk.GetImageFromArray(sat_mat)
        class11_img.CopyInformation(muslo_fat_img_slices)

        #InterMuscular + vasos + piel
        class01 = np.where (classImage == mean_classes[0,1], 1, 0)
        class01 = np.where (bone == 1, 0, class01).astype(np.float64)
        class01_img= sitk.GetImageFromArray(class01)
        class01_img.CopyInformation(muslo_fat_img_slices)

        #Skin class01
        suma = (sat_mat + class01)
        filled_suma  = sp.ndimage.binary_fill_holes(suma, structure=np.ones((1,3,2)))
        invert_filled = util.invert(filled_suma).astype(np.int32)
        dilate = morphology.dilation (invert_filled, morphology.ball(3))
        skin_class01 = np.multiply (dilate, class01)
      
        class01_withoutSkin = np.where (skin_class01 == 1, 0, class01)
      
        #Musculo
        class21 = np.where (classImage == mean_classes[2,1], 1, 0)
        class21_clean = (class21*filled_thigh_mask) .astype(np.float64)
        class21_img= sitk.GetImageFromArray(class21_clean)
        class21_img.CopyInformation(muslo_fat_img_slices)

        #Skin class21
        skin_mt =  np.multiply(dilate, class21_clean)
        mt_withoutSkin = np.where (skin_mt == 1, 0, class21_clean).astype(np.float64)
        mt_withoutSkin_img= sitk.GetImageFromArray(mt_withoutSkin)
        mt_withoutSkin_img.CopyInformation(muslo_fat_img_slices)

        #Suma de class01 y class21 para hallar area de MT
        suma = class01_withoutSkin + mt_withoutSkin 
        suma_mat_close = close_reconstruction (suma, morphology.ball(1), 2)
        suma_mat_clean = open_reconstruction(suma_mat_close, morphology.ball(3), 2)
        suma_mat_clean = suma_mat_clean.astype(np.int32)

        #Hallo la componenete conexa --> separar la grasa intermuscular de la subcutánea
        suma_mat_clean = morphology.dilation (suma_mat_clean, morphology.ball(6)) #4
        suma_mat_clean_close= morphology.closing(suma_mat_clean, morphology.ball(5)).astype(np.float64)
        suma_mat_clean_close_img = sitk.GetImageFromArray(suma_mat_clean_close)
        suma_mat_clean_close_img.CopyInformation(muslo_fat_img_slices)
        #Paso a 2D para hacer el convex hull
        suma_mat_clean_close = suma_mat_clean_close.reshape((-1, muslo_water_mat.shape[2]))
        class21_convex_hull_mat = morphology.convex_hull_object(suma_mat_clean_close).astype(np.int32)
        class21_convex_hull_mat = class21_convex_hull_mat.reshape(muslo_water_mat.shape)
        class21_convex_hull_mat = class21_convex_hull_mat.astype(np.float64)
        class21_convex_hull_img = sitk.GetImageFromArray(class21_convex_hull_mat)
        class21_convex_hull_img.CopyInformation(muslo_fat_img_slices)

        #Contorno activo
        Act_cont_IMAT = act_cont(muslo_water_img_slices, class21_convex_hull_img, -1.0, 1.5, 1.5, 1.5, -2.0, 7 , RangeSlice)
        #-2.0, 1.5, 1.5, 1.5, -1.0, 7
        Act_cont_IMAT_mat = sitk.GetArrayFromImage(Act_cont_IMAT)
       
        #Defino las diferentes componentes
        imat_mat = np.multiply(sat_withoutBone,Act_cont_IMAT_mat)
        vasos_class01_mat = np.where(Act_cont_IMAT_mat == 0, class01_withoutSkin, 0)
        vasos_mt_mat = np.where(Act_cont_IMAT_mat == 0, mt_withoutSkin, 0)
        vasos_mat = vasos_mt_mat+vasos_class01_mat
        vasos_mat = vasos_mat.astype(np.float64)
        vasos_img = sitk.GetImageFromArray(vasos_mat)
        vasos_img.CopyInformation(muslo_fat_img_slices)

        mt_withoutSkinAndBone = np.where(bone==1,0, mt_withoutSkin)

        skin = skin_class01+skin_mt

        #LABELMAP
        classImage_bw = np.zeros(muslo_water_mat.shape)
        classImage_bw[sat_withoutBone==1] = 15 #SAT
        classImage_bw[imat_mat == 1] = 31 #IMAT
        classImage_bw[mt_withoutSkinAndBone== 1] = 8 #MT 
        classImage_bw[class01_withoutSkin==1] = 11 #INTRA
        classImage_bw[vasos_mat==1] = 5 #vasos
        classImage_bw[bone == 1] = 2 #bone
        classImage_bw[marrow == 1] = 7 #marrow
        classImage_bw[skin == 1] = 6 #skin
        classImage_bw [filled_thigh_mask == 0] = 0
        classImage_bw = classImage_bw.astype(np.float64)
        classImage_bw_img  =sitk.GetImageFromArray(classImage_bw)
        classImage_bw_img.CopyInformation(muslo_fat_img_slices)
       
        return classImage_bw_img
def ThighSegmentation (fat_img, water_img, RangeSlice, numberOfPartitions, incomplete):
    '''
        Calculo de algunas máscaras necesarias para la segmentación y separación de ambos muslos

        Inputs:
            fat_img -- imagen de grasa que se desea segmentar
            water_img -- imagen de agua que se desea segmentar 
            numberOfPartitions-- conjunto de cortes en que se desea hacer la segmenatción
            RangeSlices --  rango de cortes de la imagen que se desea segmentar
            incomplete -- variable booleana que indica si se desea segmentar los muslos incompletos
            

        Outputs:
            out_l, out_r -- segmentacion de los muslos izquierdo y derecho
            right_full_Q, left_full_Q -- variables booleanas que indican si el muslo izquierdo y derecho tocan el borde, es decir, son incompletos
            sum_right, sum_left -- variables que indican si los muslos se han podido dividir
    '''

    print('Processing with TisSegLibrary '+version)

    muslo_fat_img_slices = fat_img[:,:, int(RangeSlice[0]):int(RangeSlice[1])]
    muslo_fat_mat = sitk.GetArrayFromImage(muslo_fat_img_slices)

    muslo_water_img_slices = water_img[:,:,int(RangeSlice[0]):int(RangeSlice[1])]
    muslo_water_mat = sitk.GetArrayFromImage(muslo_water_img_slices)

    numberOfPartitions=int(numberOfPartitions)

    musloShape = fat_img.GetSize()
    ultimosSlices = musloShape[2] - (musloShape[2]*10//100)
    primerosSlices = (musloShape[2]*10//100)
        
    sum_left = 2
    sum_right = 2

    muslo_fat_adjustgamma = exposure.adjust_gamma(muslo_fat_mat, 0.65)
    muslo_fat_adjustgamma_img = sitk.GetImageFromArray(muslo_fat_adjustgamma)
    muslo_fat_adjustgamma_img.CopyInformation(muslo_water_img_slices)
    muslo_water_adjustgamma = exposure.adjust_gamma(muslo_water_mat, 0.7)
    muslo_water_adjustgamma_img = sitk.GetImageFromArray(muslo_water_adjustgamma)
    muslo_water_adjustgamma_img.CopyInformation(muslo_water_img_slices)

    classImage_img, mean_classes = cluster(muslo_water_adjustgamma_img, 3, numberOfPartitions, RangeSlice, 
                                        primerosSlices, ultimosSlices,   muslo_fat_adjustgamma_img)

    classImage = sitk.GetArrayFromImage(classImage_img)
    muslo_fat_mat = sitk.GetArrayFromImage(muslo_fat_img_slices)

    #Definición de máscaras
    thigh_mask_mat= np.zeros(muslo_fat_mat.shape)
    thigh_mask_mat [classImage!=mean_classes[2,1]]= 1 
    thigh_mask_img = sitk.GetImageFromArray(thigh_mask_mat)
    thigh_mask_img.CopyInformation(muslo_fat_img_slices)

    #Relleno hueco del hueso
    filled_thigh_mask = sp.ndimage.binary_fill_holes(thigh_mask_mat, structure=np.ones((1,7,7))).astype(np.int32)
    filled_thigh_mask_img = sitk.GetImageFromArray(filled_thigh_mask)
    filled_thigh_mask_img.CopyInformation(muslo_fat_img_slices)

    #Separación de los muslos
    filled_thigh_mask_img = sitk.BinaryOpeningByReconstruction(filled_thigh_mask_img,kernelRadius=[7,7,7])
    compo_filter = sitk.ConnectedComponentImageFilter()
    compo_result = compo_filter.Execute(filled_thigh_mask_img)
    compo_num = compo_filter.GetObjectCount()
    if compo_num > 2:
        slicer.util.errorDisplay('Error detecting thighs') 

    dist_img = sitk.SignedMaurerDistanceMap(filled_thigh_mask_img != 0, insideIsPositive=False, squaredDistance=False, useImageSpacing=False)

    min_dst = np.min(np.concatenate(sitk.GetArrayFromImage(dist_img)))
    inc_radius = -0.05
    init_radius = 0.95
    actual_radius = init_radius
    while True:
        radius = actual_radius*np.abs(min_dst)
        # Seeds have a distance of "radius" or more to the object boundary, they are uniquely labelled.
        seeds = sitk.ConnectedComponent(dist_img < -radius)
        # Relabel the seed objects using consecutive object labels while removing all objects with less than 15 pixels.
        seeds = sitk.RelabelComponent(seeds, minimumObjectSize=15)
        num_comp_seeds = np.max(np.concatenate(sitk.GetArrayFromImage(seeds)))
        if num_comp_seeds<2:
            actual_radius = actual_radius+inc_radius
        else:
            break

    # Run the watershed segmentation using the distance map and seeds.
    ws = sitk.MorphologicalWatershedFromMarkers(dist_img, seeds, 
        markWatershedLine=False) 
    ws = sitk.Mask( ws, sitk.Cast(filled_thigh_mask_img, ws.GetPixelID()))


    #definición del muslo izquierdo y derecho

    #Hallo los centroides de las componentes de la watersed segmentation
    stats = sitk.LabelShapeStatisticsImageFilter()
    stats.Execute(sitk.ConnectedComponent(ws))
    numberofcompo = int (stats.GetNumberOfLabels())
    #hallo centroide de una de las componentes
    centroids = [ stats.GetCentroid(l) for l in stats.GetLabels() ]
    stats.Execute (sitk.ConnectedComponent(ws==1))
    centroid_1 = [ stats.GetCentroid(l) for l in stats.GetLabels() ]
    #hallo centroide de la otra componente
    stats.Execute (sitk.ConnectedComponent(ws==2))
    centroid_2 = [ stats.GetCentroid(l) for l in stats.GetLabels() ]

    #Si solo hay una componente, el muslo izquierdo sera el de la componente que tenga el centroide menor que el de la imagen ws
    #Y el derecho será el de la componente que tenga el centroide mayor
    if numberofcompo ==1:
        if centroid_1 > centroids and centroid_2 < centroids:
            right_mask = (ws==2)
            left_mask = (ws ==1)

        if centroid_1 < centroids and centroid_2 > centroids:
            right_mask = (ws==1)
            left_mask = (ws ==2)

    elif numberofcompo == 2:
        #Si hay dos componentes el muslo de la izquierda será el que tenga una componente menor o igual a la menor componente de la imagen ws
        #Y el muslo de la sera sera el que tenga una componente mayor o igual a la mayor componente de la imagen ws
        if centroid_1[0] <= centroids[0] and centroids[1] >= centroid_2[0]:
            if centroids[0]<centroids[1]:
                right_mask = (ws==1)
                left_mask = (ws==2)
            else:
                right_mask = (ws==2)
                left_mask = (ws==1)

        elif centroid_1[0] <= centroids[1] and  centroids[0] >= centroid_2[0]:
            if centroids[0]<centroids[1]:
                right_mask = (ws==2)
                left_mask = (ws==1)
            else:
                right_mask = (ws==1)
                left_mask = (ws==2)

    #Diferenciamos los muslos que estan pegando al borde de los que no
    clean_right_mask, right_full_Q = clean_border_thigh(right_mask,muslo_water_img_slices, muslo_fat_img_slices)
    clean_left_mask, left_full_Q = clean_border_thigh(left_mask,muslo_water_img_slices, muslo_fat_img_slices)

    if right_full_Q == True and left_full_Q == False:
        if incomplete == False:
            out_l = clean_left_mask
            
            
        else:
            out_l = CalculateLabelMap (left_mask, thigh_mask_img, muslo_fat_img_slices, muslo_water_img_slices,\
                                numberOfPartitions, RangeSlice, primerosSlices, ultimosSlices)
            

        out_r = CalculateLabelMap (clean_right_mask, thigh_mask_img, muslo_fat_img_slices, muslo_water_img_slices,\
                            numberOfPartitions, RangeSlice, primerosSlices, ultimosSlices)
        

    elif right_full_Q == False and left_full_Q == True:
        if incomplete == False:
            out_r = clean_right_mask

        else:
            out_r = CalculateLabelMap (right_mask, thigh_mask_img, muslo_fat_img_slices, muslo_water_img_slices,\
                            numberOfPartitions, RangeSlice, primerosSlices, ultimosSlices)

        out_l = CalculateLabelMap (clean_left_mask, thigh_mask_img, muslo_fat_img_slices, muslo_water_img_slices,\
                            numberOfPartitions, RangeSlice, primerosSlices, ultimosSlices)

    elif right_full_Q == True and left_full_Q == True:
        out_r = CalculateLabelMap (clean_right_mask, thigh_mask_img, muslo_fat_img_slices, muslo_water_img_slices,\
                            numberOfPartitions, RangeSlice, primerosSlices, ultimosSlices)

        out_l = CalculateLabelMap (clean_left_mask, thigh_mask_img, muslo_fat_img_slices, muslo_water_img_slices,\
                            numberOfPartitions, RangeSlice, primerosSlices, ultimosSlices)
        
    elif right_full_Q == False and left_full_Q == False:
        if incomplete == True:
            right_mask_mat = sitk.GetArrayFromImage(right_mask)
            left_mask_mat = sitk.GetArrayFromImage(left_mask)

            sum_right = np.sum(np.concatenate(right_mask_mat))
            sum_left =  np.sum(np.concatenate(left_mask_mat))
        
            if sum_right ==0 and sum_left!=0:
                out_l = CalculateLabelMap (left_mask, thigh_mask_img, muslo_fat_img_slices, muslo_water_img_slices,\
                                    numberOfPartitions, RangeSlice, primerosSlices, ultimosSlices)                
                
                out_r = clean_right_mask 

            elif sum_left==0 and sum_right!=0:
                out_r = CalculateLabelMap (right_mask, thigh_mask_img, muslo_fat_img_slices, muslo_water_img_slices,\
                                    numberOfPartitions, RangeSlice, primerosSlices, ultimosSlices)
            
                out_l = clean_left_mask 
            
            elif sum_left!=0 and sum_right!=0:

                out_r = CalculateLabelMap(right_mask, thigh_mask_img, muslo_fat_img_slices, muslo_water_img_slices,\
                                    numberOfPartitions, RangeSlice, primerosSlices, ultimosSlices)
                

                out_l = CalculateLabelMap(left_mask, thigh_mask_img, muslo_fat_img_slices, muslo_water_img_slices,\
                                    numberOfPartitions, RangeSlice, primerosSlices, ultimosSlices)
        else:
            out_l = left_mask    
            out_r = right_mask   

    return out_l, out_r, right_full_Q, left_full_Q, sum_right, sum_left

def AbdomenSegmentation( fat_img, water_img , roi_img, RangeSlice_Abdo, numberOfPartitions_Abdo):
    """
    Crea un label map con la segmentación del abdomen

    Inputs:
        fat_img -- imagen de grasa que se desea segmentar
        water_img_slices -- imagen de agua que se desea segmentar 
        roi_img -- ROI dibujada manualmente por el ususario
        numberOfPartitions_Abdo -- conjunto de cortes en que se desea hacer la segmenatción
        RangeSlices_Abdo --  rango de cortes de la imagen que se desea segmentar

    Outputs:
        classImage2_img -- label map con el resulatado de la segmenatción
    """

    print('Processing with TisSegLibrary '+version)

    abdomen_fat_img_slices = fat_img[:,:, int(RangeSlice_Abdo[0]):int(RangeSlice_Abdo[1])]
    abdomen_water_img_slices = water_img[:,:,int(RangeSlice_Abdo[0]):int(RangeSlice_Abdo[1])]
    abdomen_ROI_slices = roi_img[:,:,int(RangeSlice_Abdo[0]):int(RangeSlice_Abdo[1])]
    abdomen_fat_mat = sitk.GetArrayFromImage(abdomen_fat_img_slices)
    abdomen_water_mat = sitk.GetArrayFromImage(abdomen_water_img_slices)
    abdomen_roi_mat = sitk.GetArrayFromImage (abdomen_ROI_slices)

    numberOfPartitions_Abdo=int(numberOfPartitions_Abdo)

    abdomenShape = fat_img.GetSize()
    ultimosSlices_Abdo = abdomenShape[2] - (abdomenShape[2]*10//100)
    primerosSlices_Abdo = (abdomenShape[2]*10//100)

    #umbralizacion y limpieza
    OtsuFilter = sitk.OtsuThresholdImageFilter()
    OtsuFilter.SetInsideValue(0)
    OtsuFilter.SetOutsideValue(1)
    thresh_img = OtsuFilter.Execute(abdomen_fat_img_slices)

    adap_thres_open = sitk.BinaryOpeningByReconstruction(thresh_img , kernelRadius = [6,6,6])
    adap_thres_open_mat = sitk.GetArrayFromImage(adap_thres_open)
    adap_thres_open.CopyInformation(abdomen_fat_img_slices)

    #Convex hull para hallar el area del abdomen
    adap_thres_open_mat_re = adap_thres_open_mat.reshape((-1, adap_thres_open_mat.shape[2]))
    filled = morphology.convex_hull_object(adap_thres_open_mat_re).astype(np.int32)
    filled=filled.reshape (abdomen_fat_mat.shape)
    filled_dilate= morphology.dilation ( filled, morphology.ball(1)).astype(np.float64)
    filled_img = sitk.GetImageFromArray(filled_dilate)
    filled_img.CopyInformation(abdomen_fat_img_slices)

    #Contorno activo, para definir borde exterior del abdomen
    filled_img = act_cont (abdomen_fat_img_slices, filled_img, -7.0, 1.5 ,1.5, 1.0, -2.0, 9, RangeSlice_Abdo)
    filled = sitk.GetArrayFromImage(filled_img)

    #PRE-PROCESADO MORPFOLÓGICO
    fat_open = sitk.OpeningByReconstruction(abdomen_fat_img_slices , kernelRadius = [6,6,6])
    print('fat open', fat_open.GetSize())
    print('fat img', fat_img.GetSize())

    #Contorno activo de la ROI
    ROI_acti =act_cont(fat_open, abdomen_ROI_slices, -0.185, 0.7, 0.7, 1.0, -7, 13, RangeSlice_Abdo)
    ROI_acti.CopyInformation(abdomen_fat_img_slices)
    ROI_acti_mat = sitk.GetArrayFromImage(ROI_acti)
    
    #Calculo FF
    abdomen_fat_eps =np.where(abdomen_fat_mat==0, np.finfo(float).eps, abdomen_fat_mat)  #Así evitamos el 0/0
    abdomen_water_eps =np.where(abdomen_water_mat==0, np.finfo(float).eps, abdomen_water_mat)  #Así evitamos el 0/0
    FF_mat = np.divide(abdomen_fat_eps, (abdomen_fat_eps+abdomen_water_eps)) 
    FF_clean = np.multiply (FF_mat, filled)
    FF_img =sitk.GetImageFromArray(FF_clean)
    FF_img.CopyInformation(abdomen_fat_img_slices)

    #K-Means de FF
    classImage_img, brillo = cluster(FF_img, 3,numberOfPartitions_Abdo, RangeSlice_Abdo, 
                            primerosSlices_Abdo, ultimosSlices_Abdo, mask= filled_img, centroids=np.array([[0.1], [1], [0.5]]))

    classImage = sitk.GetArrayFromImage(classImage_img)

    #Defino los diferentes clusters
    class01 = np.where (classImage == brillo[0,1], 1, 0).astype(np.float64)
    class01_img= sitk.GetImageFromArray(class01)
    class01_img.CopyInformation(abdomen_fat_img_slices)

    class11 = np.where (classImage == brillo[1,1], 1, 0).astype(np.float64)
    class11_img= sitk.GetImageFromArray(class11)
    class11_img.CopyInformation(abdomen_fat_img_slices)

    class21 = np.where (classImage == brillo[2,1], 1, 0)
    class21_clean = np.multiply(class21, filled).astype(np.float64)
    class21_img= sitk.GetImageFromArray(class21_clean)
    class21_img.CopyInformation(abdomen_fat_img_slices)

    #Caculo contorno interior de SAT y hallo edema y vasos
    class11_img = sitk.Cast(class11_img, sitk.sitkFloat32)
    ROI_acti = sitk.Cast(ROI_acti, sitk.sitkFloat32)

    #Selecciono el SAT
    class11_sinROI_img = class11_img -ROI_acti
    class11_sinROI = sitk.GetArrayFromImage(class11_sinROI_img)
    class11_sinROI = np.where (class11_sinROI<0, 0, class11_sinROI)
    class11_sinROI =class11_sinROI * filled
    class11_sinROI = class11_sinROI.astype(np.float64)
    class11_sinROI_img_clean = sitk.GetImageFromArray(class11_sinROI)
    class11_sinROI_img_clean.CopyInformation(abdomen_fat_img_slices)

    #Limpieza de la zona interior  y relleno de los posibles edemas
    class11_sinROI_img_clean = sitk.Cast(class11_sinROI_img_clean, sitk.sitkInt32)
    class11_sinROI_mat_clean = sitk.GetArrayFromImage(class11_sinROI_img_clean)
    class11_sinROI_mat_clean = morphology.opening(class11_sinROI_mat_clean, morphology.ball(2)).astype(np.float64)
    class11_sinROI_img_clean = sitk.GetImageFromArray(class11_sinROI_mat_clean)
    class11_sinROI_img_clean.CopyInformation(abdomen_fat_img_slices)
    class11_sinROI_img_clean = sitk.Cast(class11_sinROI_img_clean, sitk.sitkInt32)

    class11_sinROI_open = sitk.BinaryOpeningByReconstruction(class11_sinROI_img_clean, kernelRadius = [5,5,5])
    class11_sinROI_open.CopyInformation(abdomen_fat_img_slices)

    class11_sinROI_open_mat = sitk.GetArrayFromImage(class11_sinROI_open)
    class11_sinROI_open_close_mat = morphology.closing (class11_sinROI_open_mat, morphology.ball(2))
    
    class11_sinROI_filled = morphology.closing (class11_sinROI_open_close_mat, morphology.ball(5)).astype(np.float64) #este es para rellenar el edema
    class11_sinROI_filled_img = sitk.GetImageFromArray(class11_sinROI_filled)
    class11_sinROI_filled_img.CopyInformation(abdomen_fat_img_slices)
    class11_sinROI_filled_img = sitk.Cast(class11_sinROI_filled_img, sitk.sitkInt32)
    #Selecciona la zona interior (no selecciono el edema)
    Out_erosion  =morphology.erosion (filled, morphology.ball(5)).astype(np.float64)
    BWGmA_incom = util.invert((adap_thres_open_mat).astype(np.float32)).astype(np.float64)
    Out_erosion_img = sitk.GetImageFromArray(Out_erosion)
    Out_erosion_img.CopyInformation(abdomen_fat_img_slices)
    BWGmA_inco_img = sitk.GetImageFromArray(BWGmA_incom)
    BWGmA_inco_img.CopyInformation(abdomen_fat_img_slices)

    multi = np.multiply (BWGmA_incom, Out_erosion).astype(np.float64)
    multi_img = sitk.GetImageFromArray(multi)
    multi_img.CopyInformation(abdomen_fat_img_slices)
    multi_img = sitk.Cast(multi_img, sitk.sitkInt32)
    closing =sitk.BinaryClosingByReconstruction ( multi_img, kernelRadius = [7,7,7])
    opening =sitk.BinaryOpeningByReconstruction ( closing, kernelRadius = [3,3,3])

    interse = opening & class11_sinROI_filled_img
    interior = opening - interse

    #Convex hull
    opening_mat = sitk.GetArrayFromImage(interior)
    opening_mat =morphology.closing (opening_mat, morphology.ball(7))
    opening_mat = opening_mat.reshape((-1, opening_mat.shape[2]))
    convex_hull =  morphology.convex_hull_object(opening_mat).astype(np.int32)
    convex_hull = convex_hull.reshape(abdomen_fat_mat.shape)
    convex_hull_dilate = morphology.dilation (convex_hull, morphology.ball(2.5)).astype(np.float64)
    convex_img = sitk.GetImageFromArray(convex_hull_dilate)
    convex_img.CopyInformation(abdomen_fat_img_slices)

    #Contornos activos, definir contorno interior del SAT
    active_cont = act_cont (fat_open, convex_img, -3.0, 0.35, 0.35, 1.5, -6.0, 9, RangeSlice_Abdo)
    active_cont.CopyInformation(abdomen_fat_img_slices)
    active_mat = sitk.GetArrayFromImage(active_cont)

    #DEINO LAS COMPONENTES
    #SAT
    SAT = np.where ( active_mat==1, 0, filled).astype(np.float64)
    SAT_img = sitk.GetImageFromArray(SAT)
    SAT_img.CopyInformation(abdomen_fat_img_slices)

    #IMAT
    IMAT_area = xor (ROI_acti_mat.astype(np.bool_),  active_mat.astype(np.bool_) ).astype(np.float64)
    IMAT = np.where (classImage*IMAT_area == brillo[1,1], 1, 0).astype(np.float64)
    IMAT_img = sitk.GetImageFromArray(IMAT)
    IMAT_img.CopyInformation(abdomen_fat_img_slices)

    #BONE
    BoneAndFat = np.where (classImage==brillo[0,1], 1, 0).astype(np.float64)
    BoneAndFat_img = sitk.GetImageFromArray(BoneAndFat)
    BoneAndFat_img.CopyInformation(abdomen_fat_img_slices)
    Bone = IMAT_area * BoneAndFat
    Bone = Bone.astype(np.float64)
    Bone_img = sitk.GetImageFromArray(Bone)
    Bone_img.CopyInformation(abdomen_fat_img_slices)

    #MT
    MT = class21_clean.astype(np.float64)
    MT_img = sitk.GetImageFromArray(MT)
    MT_img.CopyInformation(abdomen_fat_img_slices)

    #VAT
    VAT_area = classImage*ROI_acti_mat
    VAT = np.where (VAT_area > 0, 1, 0).astype(np.float64)
    VAT_img = sitk.GetImageFromArray(VAT)
    VAT_img.CopyInformation(abdomen_fat_img_slices)

    #AIR
    ROI_erode = morphology.erosion (ROI_acti_mat, morphology.ball(1.5)).astype(np.float32)
    air = (VAT_area * BoneAndFat).astype(np.bool_)
    air = air * ROI_erode
    air = air.astype(np.float64)
    air_img = sitk.GetImageFromArray(air.astype(np.int32))
    air_img.CopyInformation(abdomen_fat_img_slices)

    #OTHER TISSUE
    Other_tissue = np.multiply(class21_clean, ROI_erode).astype(np.float64)
    Other_tissue_img = sitk.GetImageFromArray(Other_tissue)
    Other_tissue_img.CopyInformation(abdomen_fat_img_slices)

    #SKIN
    filled_erode = morphology.erosion (filled, morphology.ball(7)).astype(np.float32)
    Skin_class01 = util.invert(filled_erode) * (class01)
    Skin_class21 = util.invert(filled_erode) * (class21)
    Skin = (Skin_class01 + Skin_class21)* filled
    Skin = Skin.astype(np.float64)
    Skin_img = sitk.GetImageFromArray(Skin)
    Skin_img.CopyInformation(abdomen_fat_img_slices)

    #EDEMA + VESSELS
    suma_classes = (class01_img + class21_img) - Skin_img
    active_mat_dilate = morphology.dilation(active_mat, morphology.ball(2))
    aux =active_mat_dilate + ROI_acti_mat
    active_mat_invert = util.invert(aux.astype(np.float32)).astype(np.float64)
    active_invert_img = sitk.GetImageFromArray(active_mat_invert)
    active_invert_img.CopyInformation(abdomen_fat_img_slices)
    edema_img = suma_classes * active_invert_img
    edema = sitk.GetArrayFromImage(edema_img)

    classImage2 = np.zeros (abdomen_fat_mat.shape)
    classImage2[filled == 1] = 15 #SAT
    classImage2[IMAT == 1] = 31 #IMAT
    classImage2[VAT == 1] = 11 #VAT
    classImage2[MT==1] = 8  #MT
    classImage2[Other_tissue == 1]= 5 #OTHER TISSUE
    classImage2[Bone == 1] = 2 #BONE/AIR
    classImage2[air==True] = 7 #AIR
    classImage2[Skin == 1] = 6 #SKIN
    classImage2[edema == 1] = 36 #EDEMA+VESSELS
    classImage2 = classImage2.astype(np.float64)
    classImage2_img=sitk.GetImageFromArray(classImage2)
    classImage2_img.CopyInformation(abdomen_fat_img_slices)

    return classImage2_img

def ColorSegmentation_Abdo(outputVolume, Segmentation):
        """
        Convierte un label map en segmenatción. También define el color y nombra cada uno de los segmentos de la segmenatcaión

        Parámetros:
            outputVolume -- label map a partir del que se obtiene la  segmentación
            Segmentation -- volumen que contine la segmentación
        """
        if Segmentation is not None:
            #Se eliminan los posibles segmentos que exitan
            segmentation = Segmentation.GetSegmentation()
            segmentation.RemoveAllSegments()
            #Se importa el label map a una segmentacion y se define (nombre y color) cada segmento
            slicer.modules.segmentations.logic().ImportLabelmapToSegmentationNode(outputVolume, Segmentation)
            segmentation = Segmentation.GetSegmentation()
            if  segmentation.GetNumberOfSegments () >= 8 and segmentation.GetNumberOfSegments () < 10 :
                segment = segmentation.GetNthSegment(6)
                segment.SetName("SAT")
                color = (230,220,70)
                color = np.array(color, float) / 255
                segment.SetColor(color)
                segment = segmentation.GetNthSegment(7)
                segment.SetName("IMAT")
                color = (140,224,228)
                color = np.array(color, float) / 255
                segment.SetColor(color)
                segment = segmentation.GetNthSegment(4)
                segment.SetName("Muscle")
                color = (192,104,88)
                color = np.array(color, float) / 255
                segment.SetColor(color)
                segment = segmentation.GetNthSegment(5)
                segment.SetName("VAT")
                color = (250,250,225)
                color = np.array(color, float) / 255
                segment.SetColor(color)
                segment = segmentation.GetNthSegment(3)
                segment.SetName("Air")
                color = (144,238,144) 
                color = np.array(color, float) / 255
                segment.SetColor(color)
                segment = segmentation.GetNthSegment(0)
                segment.SetName("Bone/Air")
                color = (241,214, 145)
                color = np.array(color, float) / 255
                segment.SetColor(color)
                segment = segmentation.GetNthSegment(1)
                segment.SetName("Other tissue")
                color = (216 ,101,79)
                color = np.array(color, float) / 255
                segment.SetColor(color)
                segment = segmentation.GetNthSegment(2)
                segment.SetName("Skin")
                color = (177,122,101)
                color = np.array(color, float) / 255
                segment.SetColor(color)
                segment = segmentation.GetNthSegment(8)
                segment.SetName("Edema + Vessels")
                color = (150,98,83)
                color = np.array(color, float) / 255
                segment.SetColor(color)
                
                Segmentation.CreateClosedSurfaceRepresentation()
            else:
                slicer.util.errorDisplay ("The segmentation couldn't be done correctly")
def ColorSegmentation(outputVolume, l_o_r, Segmentation):
        """
        Convierte un label map en segmenatción. También define el color y nombra cada uno de los segmentos de la segmenatcaión

        Parámetros:
            outputVolume -- label map a partir del que se obtiene la  segmentación
            Segmentation -- volumen que contine la segmentación
        """

        if Segmentation is not None:
            #Se eliminan los posibles segmentos que exitan
            segmentation = Segmentation.GetSegmentation()
            segmentation.RemoveAllSegments()
            #Se importa el label map a una segmentacion y se define (nombre y color) cada segmento
            slicer.modules.segmentations.logic().ImportLabelmapToSegmentationNode(outputVolume, Segmentation)
            segmentation = Segmentation.GetSegmentation()
            if  segmentation.GetNumberOfSegments () == 8:
                segment = segmentation.GetNthSegment(6)
                segment.SetName("SAT"+ l_o_r)
                color = (230,220,70)
                color = np.array(color, float) / 255
                segment.SetColor(color)
                segment = segmentation.GetNthSegment(7)
                segment.SetName("InterMAT"+ l_o_r)
                color = (140,224,228)
                color = np.array(color, float) / 255
                segment.SetColor(color)
                segment = segmentation.GetNthSegment(4)
                segment.SetName("Muscle"+ l_o_r)
                color = (192,104,88)
                color = np.array(color, float) / 255
                segment.SetColor(color)
                segment = segmentation.GetNthSegment(5)
                segment.SetName("IntraMAT"+ l_o_r)
                color = (250,250,225)
                color = np.array(color, float) / 255
                segment.SetColor(color)
                segment = segmentation.GetNthSegment(1)
                segment.SetName("Vessels"+ l_o_r)
                color = (216 ,101,79)
                color = np.array(color, float) / 255
                segment.SetColor(color)
                segment = segmentation.GetNthSegment(0)
                segment.SetName("Bone"+ l_o_r)
                color = (241,214, 145)
                color = np.array(color, float) / 255
                segment.SetColor(color)
                segment = segmentation.GetNthSegment(3)
                segment.SetName("Marrow"+ l_o_r)
                color = (144,238,144)
                color = np.array(color, float) / 255
                segment.SetColor(color)
                segment = segmentation.GetNthSegment(2)
                segment.SetName("Skin"+ l_o_r)
                color = (177,122,101)
                color = np.array(color, float) / 255
                segment.SetColor(color)
                Segmentation.CreateClosedSurfaceRepresentation()
            else:
                    slicer.util.errorDisplay ("The segmentation couldn't be done correctly")