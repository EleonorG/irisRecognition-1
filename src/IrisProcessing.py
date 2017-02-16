import numpy as np
import cv2
import math
#import scipy.integrate as integrate

def captureVideoFromCamera():
    cap = cv2.VideoCapture(0)

    while (True):
        # Capture frame-by-frame
        ret, frame = cap.read()

        # Our operations on thqe frame come here
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        tryToShowPupil(gray)
        # Display the resulting frame
        cv2.imshow('frame', gray)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    cap.release()
    cv2.destroyAllWindows()

#this method presents the image with some title
#image = choosed image
#title = title for choosed image
def showImage(image,title):
    cv2.imshow(title, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

#This method draw circle on respective image
#image = choosed image
#circles = array of circles to draw
#filled = boolean value that indicates if the circles will be filled with white color or not
def drawCirclesOnImage(image,circles,filled=False):
    thickness = 2
    if filled: thickness = -1
    for i in circles[0:]:
        # draw the outer circle
        cv2.circle(image, (i[0], i[1]), i[2], (255, 255, 255), thickness, 2)
        # draw the center of the circle
        cv2.circle(image, (i[0], i[1]), 2, (255, 255, 255), thickness, 3)
    return image

#Draw lines on image
#image  = choosed image
#lines = array of lines to draw
def drawLinesOnImage(image,lines):
    for rho, theta in lines[0]:
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a * rho
        y0 = b * rho
        x1 = int(x0 + 1000 * (-b))
        y1 = int(y0 + 1000 * (a))
        x2 = int(x0 - 1000 * (-b))
        y2 = int(y0 - 1000 * (a))
        cv2.line(image, (x1, y1), (x2, y2), (0, 0, 255), 2)
    return image

#Draw a rectangle on a image
#image = choosed image
#topLefPoint = the top left corner point
#width = width of rectangle
#height = height of rectangle
def drawRectangleOnImage(image,topLeftPoint,width,height,filled=False):
    thickness = 2
    if filled: thickness = -1
    bottomRightPoint = (topLeftPoint[0]+width,topLeftPoint[1]+height)
    cv2.rectangle(image,topLeftPoint,bottomRightPoint,(255,255,255),thickness)


#returns a rectangle based on parameters
#circle region
#offSetBy a tuple with some values indicating how much it should be bigger or smaller than circle
def rectangleOfCircle(circle,offSetBy=(0,0)):
    # rect with radio equal iris circle
    heightOne = int(circle[2] * 2 + offSetBy[1])
    widthOne = int(circle[2] * 2 + offSetBy[0])

    circleCenterXOne = circle[0]
    circleCenterYOne = circle[1]

    topLeftPointOne = (int(circleCenterXOne - widthOne / 2), int(circleCenterYOne - heightOne / 2))
    return [topLeftPointOne[0],topLeftPointOne[1],widthOne,heightOne]

#This method only calculates the distance between two points
def __distanceBetweenPoints(px1,py1,px2,py2):
    a = (px2 - px1) ** 2 + (py2 - py1) ** 2
    b = math.sqrt(a)
    return b

# this method return the corresponding point(x,y) for some angle on the border of circle
def __maxPointsOfCircleForAngle(circle,angle):
    r = circle[2]
    centerX = circle[0]
    centerY = circle[1]
    x = int(centerX + r * math.cos(angle * math.pi / 180))
    y = int(centerY + r * math.sin(angle * math.pi / 180))
    return(x,y)

def __pixelsOfCircle(image,circle,showProcess=False):
    lins = int(circle[2])  # int(irisCircle[2] - pupilCircle[2])
    cols = 360#int((irisCircle[2] - pupilCircle[2]) + 2)
    circleData = np.zeros((lins, cols), np.uint8)

    for ri in range(0,lins):
        line = np.zeros(360, np.uint8)
        for angle in range(0,cols):
            x = int(circle[0] + ri*math.cos(angle*math.pi/180))
            y = int(circle[1] + ri * math.sin(angle * math.pi / 180))
            line[angle] = image[y][x]
        circleData[ri] = line

    if showProcess: showImage(circleData,"Pixels on Circle")
    return circleData

#This method calculates and returns the corresponding point of circle on its border for some angle
def __pointOfCircle(circle,angle):
    rads = angle * math.pi / 180
    cosValue = math.cos(rads)
    sinValue = math.sin(rads)
    x = int(circle[0] + circle[2] * cosValue)
    y = int(circle[1] + circle[2] * sinValue)
    return [x,y]

#This method extracts the iris information
#pupilRadioOffset this value indicates how many pixels you want to increment on pupil radio to avoid the possibility
#to appear some pupil pixels
#The size of normalized image depends of irisRadio - pupilRadio, that can change because of pupil dilation for example
def __normalizeIrisRegion(eyeImage,pupilCircle,irisCircle,pupilRadioOffset=0):
    lins = int(irisCircle[2] - pupilCircle[2] - pupilRadioOffset)  # int(irisCircle[2] - pupilCircle[2])
    cols = 360#int((irisCircle[2] - pupilCircle[2]) + 2)
    irisData = np.zeros((lins, cols), np.uint8)

    xDif = irisCircle[0] - pupilCircle[0]
    yDif = irisCircle[1] - pupilCircle[1]

    for ri in range(int(pupilCircle[2] + pupilRadioOffset),irisCircle[2]):
        line = np.zeros(360, np.uint8)
        for angle in range(0,cols):
            cosValue = math.cos(angle*math.pi/180)
            sinValue = math.sin(angle * math.pi / 180)
            x = int(irisCircle[0] + (ri - xDif*cosValue)*cosValue)
            y = int(irisCircle[1] + (ri - yDif*sinValue) * sinValue)
            line[angle] = eyeImage[y][x]
        irisData[int(ri - pupilCircle[2] - pupilRadioOffset)] = line

    return irisData

#Rubber Sheet Model
# this method normalize the iris region using the same method of Daugman, so the normalized image
#always has the same dimensions fixing some problems like pupil dilation and other thing that might cause
#changes on normalized iris region image size
def __RSM_NormIrisRegion(eyeImage,pupilCircle,irisCircle,numbOfLins=10,pupilOffset=0):
    numbOfCols = 360
    irisData = np.zeros((numbOfLins, numbOfCols), np.uint8)
    for p in np.arange(0.0, 1.0, 1.0 / numbOfLins):
        line = np.zeros(numbOfCols, np.uint8)
        for angle in range(0,360,360/numbOfCols):
            pupilPoint = __pointOfCircle([pupilCircle[0],pupilCircle[1],pupilCircle[2]+pupilOffset],angle)
            irisPoint = __pointOfCircle(irisCircle,angle)
            xo = int((1-p)*pupilPoint[0] + p*irisPoint[0])
            yo = int((1-p)*pupilPoint[1] + p*irisPoint[1])
            line[angle] = eyeImage[yo][xo]
        irisData[int(p*numbOfLins)] = line
    return irisData

def __codificateIrisData(irisData):
    cols = irisData.shape[1]
    lines = irisData.shape[0]
    #irisCode = np.zeros((lines, cols), np.uint8)
    irisCode = np.zeros((lines, cols))

    for y in range(0,lines):
        #line = np.zeros(cols, np.uint8)
        line = np.zeros(cols)
        for x in range(0,cols):
            xRads = x*math.pi/180
            pixelValue = irisData[y][x]
            #f0 = irisData[y][0]
            #q = f0 + 10
            #gaborValue = math.exp(-((math.log10(pixelValue/f0))**2)/2*(math.log10(q/f0))**2)
            #line[x] = gaborValue
            w0 = 0.1
            qw = 0.55
            radialPart = math.exp(-((math.log10(pixelValue/w0))**2)/(2*(math.log10(qw))**2))

            d0 = 0
            qd = math.pi / 8
            anglePart = math.exp(-((xRads - d0)**2)/(2*(qd)**2))
            gaborValue = radialPart*anglePart
            line[x] = gaborValue
        irisCode[y] = line
    irisCode

#This method try to find iris outer countorn
#eyeImage must have the pupil paited of black
#pupilCircle = circle that represents the pupil region
def __irisCircleOnImage(blackedPupilEyeImage,pupilCircle,showProcess):
    # eyeImage.shape[0] lines
    # eyeImage.shape[1] columns
    center = (blackedPupilEyeImage.shape[0] / 2, blackedPupilEyeImage.shape[1] / 2)
    processedImage = cv2.medianBlur(blackedPupilEyeImage, 11)#11#cv2.Canny(blackedPupilEyeImage, 5, 70, 3)  # cv2.Canny(processedImage, 55, 60,3)#

    if showProcess: showImage(processedImage, "Canny Iris Image")

    #processedImage = cv2.GaussianBlur(processedImage, (9,9), 0,0)  # cv2.GaussianBlur(eyeImage, (9, 9), 2, 2)

    #if showProcess: showImage(processedImage, "Blurred Iris Image")

    i = 30
    max = 100
    bestIrisCircle = None
    while (i < max and bestIrisCircle is None):
        print "tentativa "+str(i - 30)
        objCircles = cv2.HoughCircles(processedImage, cv2.HOUGH_GRADIENT, 2, center[0] / 2, 200, i, pupilCircle[2],int(pupilCircle[2] + 20))
        if i == max - 1:
            print "teste"
        if objCircles is None:
            print"No Circles were found"
        elif objCircles.__len__() > 0:
            circles = objCircles[0]
            if circles.__len__() > 0:
                if circles.__len__() == 1:
                    bestIrisCircle = circles[0]
                else:
                    if bestIrisCircle is None:
                        bestIrisCircle = circles[0]
                    lastDistance = __distanceBetweenPoints(pupilCircle[0], pupilCircle[1], bestIrisCircle[0],
                                                             bestIrisCircle[1])
                    for k in circles:
                        d = __distanceBetweenPoints(pupilCircle[0], pupilCircle[1], k[0], k[1])
                        if d == 0 and k[2] > pupilCircle[2]:
                            return k
                        elif d < lastDistance:
                            lastDistance = d
                            bestIrisCircle = k

        i += 1

    print int(pupilCircle[2] + 20)
    print bestIrisCircle[2]
    #return bestIrisCircle
    return [pupilCircle[0],pupilCircle[1],bestIrisCircle[2]]#fixing some deviation on center

def __irisCircleOnImageV1(eyeImage,pupilCircle,showProcess=False):
    # eyeImage.shape[0] lines
    # eyeImage.shape[1] columns


    blackedPupilEyeImage = eyeImage.copy()
    drawCirclesOnImage(blackedPupilEyeImage,[pupilCircle],True)

    if showProcess: showImage(blackedPupilEyeImage, "Painted pupil")

    center = (blackedPupilEyeImage.shape[0] / 2, blackedPupilEyeImage.shape[1] / 2)
    processedImage = cv2.medianBlur(blackedPupilEyeImage, 11)
    if showProcess: showImage(processedImage, "Median Blurred Iris Image")

    i = 30
    max = 100
    bestIrisCircle = None
    while (i < max and bestIrisCircle is None):
        print "tentativa "+str(i - 30)
        objCircles = cv2.HoughCircles(processedImage, cv2.HOUGH_GRADIENT, 2, center[0] / 2, 200, i, pupilCircle[2],int(pupilCircle[2] + 20))
        if i == max - 1:
            print "teste"
        if objCircles is None:
            print"No Circles were found"
        elif objCircles.__len__() > 0:
            circles = objCircles[0]
            if circles.__len__() > 0:
                if circles.__len__() == 1:
                    bestIrisCircle = circles[0]
                else:
                    if bestIrisCircle is None:
                        bestIrisCircle = circles[0]
                    lastDistance = __distanceBetweenPoints(pupilCircle[0], pupilCircle[1], bestIrisCircle[0],
                                                             bestIrisCircle[1])
                    for k in circles:
                        d = __distanceBetweenPoints(pupilCircle[0], pupilCircle[1], k[0], k[1])
                        if d == 0 and k[2] > pupilCircle[2]:
                            return k
                        elif d < lastDistance:
                            lastDistance = d
                            bestIrisCircle = k

        i += 1

    print int(pupilCircle[2] + 20)
    print bestIrisCircle[2]
    #return bestIrisCircle
    return [pupilCircle[0],pupilCircle[1],bestIrisCircle[2]]#fixing some deviation on center
    #return [int(pupilCircle[0] + 15),int(pupilCircle[1] + 6),bestIrisCircle[2]]#fixing some deviation on center

#raspcamera
def __irisCircleOnImageRaspCam(eyeImage,pupilCircle,showProcess=False):
    blackedPupilEyeImage = eyeImage.copy()
    rect = rectangleOfCircle(pupilCircle,(2,2))
    drawRectangleOnImage(blackedPupilEyeImage,(rect[0],rect[1]),rect[2],rect[3],True)

    if showProcess: showImage(blackedPupilEyeImage, "Painted pupil")

    yInitial = int(pupilCircle[1] - 2*pupilCircle[2])
    yFinal = int(pupilCircle[1] + 2*pupilCircle[2])
    xInitial = int(pupilCircle[0] - 2*pupilCircle[2])
    xFinal = int(pupilCircle[0] + 2*pupilCircle[2])
    blackedPupilEyeImage = blackedPupilEyeImage[yInitial:yFinal,xInitial:xFinal]
    if showProcess: showImage(blackedPupilEyeImage, "cutted pupil image")


    center = (blackedPupilEyeImage.shape[0] / 2, blackedPupilEyeImage.shape[1] / 2)
    #processedImage = cv2.medianBlur(blackedPupilEyeImage, 11)
    processedImage = cv2.bilateralFilter(blackedPupilEyeImage, 30, 10, 100, 25)
    #processedImage = cv2.GaussianBlur(blackedPupilEyeImage, (9,9), 3, 3)  # change on 1_5

    #processedImage = cv2.medianBlur(blackedPupilEyeImage,11)
    #processedImage = cv2.bilateralFilter(processedImage, 30, 10, 100, 25)
    if showProcess: showImage(processedImage, "Median Blurred Iris Image")

    i = 30
    max = 100
    bestIrisCircle = None
    while (i < max and bestIrisCircle is None):
        print "tentativa "+str(i - 30)
        objCircles = cv2.HoughCircles(processedImage, cv2.HOUGH_GRADIENT, 2, center[0] / 2, 200, i, pupilCircle[2],int(pupilCircle[2] + 20))#
        if i == max - 1:
            print "teste"
        if objCircles is None:
            print"No Circles were found"
        elif objCircles.__len__() > 0:
            circles = objCircles[0]
            if circles.__len__() > 0:
                if circles.__len__() == 1:
                    bestIrisCircle = circles[0]
                else:
                    if bestIrisCircle is None:
                        bestIrisCircle = circles[0]
                    lastDistance = __distanceBetweenPoints(pupilCircle[0], pupilCircle[1], bestIrisCircle[0],
                                                             bestIrisCircle[1])
                    for k in circles:
                        d = __distanceBetweenPoints(pupilCircle[0], pupilCircle[1], k[0], k[1])
                        if d == 0 and k[2] > pupilCircle[2]:
                            return k
                        elif d < lastDistance:
                            lastDistance = d
                            bestIrisCircle = k

        i += 1

    print int(pupilCircle[2] + 20)
    print bestIrisCircle[2]

    drawCirclesOnImage(blackedPupilEyeImage,[bestIrisCircle])
    showImage(blackedPupilEyeImage,"asd")

    #return bestIrisCircle

    return np.array([bestIrisCircle[0] + xInitial,bestIrisCircle[1] + yInitial,bestIrisCircle[2]],np.float32)

    #return [pupilCircle[0],pupilCircle[1],bestIrisCircle[2]]#fixing some deviation on center

#This method tries to find the region that corresponds to pupil
def __pupilCircleOnImage(eyeImage,showProcess):
    if showProcess : showImage(eyeImage, "Original Iris Image")
    # eyeImage.shape[0] lines
    # eyeImage.shape[1] columns
    center = (eyeImage.shape[0] / 2, eyeImage.shape[1] / 2)
    aspectRatio = center[1]/center[0]
    baseKSize = 9
    blurKSize = (baseKSize,baseKSize)

    processedImage = eyeImage
    processedImage = cv2.GaussianBlur(processedImage, blurKSize, blurKSize[0]/2,blurKSize[1]/2)  # cv2.GaussianBlur(eyeImage, (9, 9), 2, 2)

    if showProcess: showImage(processedImage, "Blurred Iris Image")

    # do not offer a really good improvement
    #processedImage = cv2.Canny(processedImage, 5, 70, 3)  # cv2.Canny(processedImage, 55, 60,3)#
    #if showProcess: showImage(processedImage, "Canny Iris Image")

    print "primeira tentativa da pupila"
    # HoughCircles(gray, circles, CV_HOUGH_GRADIENT,2, gray->rows/4, 200, 100 );//center[0] / 2
    objCircles = cv2.HoughCircles(processedImage, cv2.HOUGH_GRADIENT, 2, center[0] / 2, 200, 100)
    # objCircles = cv2.HoughCircles(eyeImage, cv2.HOUGH_GRADIENT, 2, center[0] / 2, 200, 100)

    if objCircles is None:
        print "segunda tentativa da pupila"
        objCircles = cv2.HoughCircles(eyeImage, cv2.HOUGH_GRADIENT, 2, center[0] / 2, 200, 100)

    if objCircles is None:
        raise Exception("No Circles were found")
    elif objCircles.__len__() > 0:
        circles = objCircles[0]
        if circles.__len__() > 0:
            circle = circles[0]
            if circles.__len__() > 1:
                print("found "+str(circles.__len__())+" circles")
                lastDistance = __distanceBetweenPoints(center[0], center[1], circles[0][0], circles[0][1])
                for i in circles:
                    d = __distanceBetweenPoints(center[0], center[1], i[0], i[1])
                    if d < lastDistance:
                        lastDistance = d
                        circle = i
            return circle
    return objCircles

#make all initial images work
# working
def __pupilCircleOnImageV1(eyeImage,showProcess):
   return __pupilCircleOnImage(eyeImage,showProcess)


#make all initial images work on first trial
# working
def __pupilCircleOnImageV1_5(eyeImage,showProcess):
    if showProcess : showImage(eyeImage, "Original Iris Image")

    center = (eyeImage.shape[0] / 2, eyeImage.shape[1] / 2)
    baseKSize = 9
    blurKSize = (baseKSize,baseKSize)

    processedImage = eyeImage
    processedImage = cv2.GaussianBlur(processedImage, blurKSize, 3,3)# change

    if showProcess: showImage(processedImage, "Blurred Iris Image")


    print "primeira tentativa da pupila"
    objCircles = cv2.HoughCircles(processedImage, cv2.HOUGH_GRADIENT, 2, center[0] / 2, 200, 100)

    if objCircles is None:
        print "segunda tentativa da pupila"
        objCircles = cv2.HoughCircles(eyeImage, cv2.HOUGH_GRADIENT, 2, center[0] / 2, 200, 100)

    if objCircles is None:
        raise Exception("No Circles were found")
    elif objCircles.__len__() > 0:
        circles = objCircles[0]
        if circles.__len__() > 0:
            circle = circles[0]
            if circles.__len__() > 1:
                print("found "+str(circles.__len__())+" circles")
                lastDistance = __distanceBetweenPoints(center[0], center[1], circles[0][0], circles[0][1])
                for i in circles:
                    d = __distanceBetweenPoints(center[0], center[1], i[0], i[1])
                    if d < lastDistance:
                        lastDistance = d
                        circle = i
            return circle
    return objCircles

#make all other images work
# this is for casia images
def __pupilCircleOnImageV2(eyeImage,showProcess=False):
    width = eyeImage.shape[1]
    height = eyeImage.shape[0]
    average = np.median(eyeImage)
    center = (width / 2, height / 2)  # change on 2 fixing

    if showProcess : showImage(eyeImage, "Original Iris Image")

    baseKSize = 9
    blurKSize = (baseKSize,baseKSize)
    #radius = width - 50
    #if height < width: radius = height
    #cv2.circle(processedImage, center, radius/2, (0, 0, 0), -1, 8,0)
    #cv2.ellipse(processedImage,center,(radius/2,radius/3),0,0,360,(255, 255, 255),-1,8)
    #cv2.rectangle(processedImage,(center[0] - radius/2,center[1] - radius/2),(center[0] + radius/2,center[1] + radius/2),(255, 255, 255),-1,8)
    #processedImage = eyeImage - processedImage
    #if showProcess: showImage(processedImage, "cutted Iris Image")

    # // Homogeneous
    # blur:
    # blur(image, dstHomo, Size(kernel_length, kernel_length), Point(-1, -1));
    # // Gaussian
    # blur:
    # GaussianBlur(image, dstGaus, Size(kernel_length, kernel_length), 0, 0);
    # // Median
    # blur:
    # medianBlur(image, dstMed, kernel_length);
    # // Bilateral
    # blur:
    # bilateralFilter(image, dstBila, kernel_length, kernel_length * 2, kernel_length / 2);

    print "primeira tentativa da pupila"

    processedImage = cv2.GaussianBlur(eyeImage, blurKSize, 3,3)# change on 1_5
    #processedImage = cv2.bilateralFilter(processedImage,30,50,100,25)
    #processedImage  = cv2.medianBlur(processedImage,7)
    #processedImage = cv2.blur(processedImage,(5,5),(-1,-1))

    if showProcess: showImage(processedImage, "Gaussian Blurred Iris Image")

    #average = np.median(processedImage)
    #processedImage = cv2.inRange(processedImage,0,average)#inRange(original, Scalar(30,30,30), Scalar(80,80,80), mask_pupil);
    #if showProcess: showImage(processedImage, "Teste Image")

    # # do not offer a really good improvement
    # v = np.median(eyeImage)
    # # apply automatic Canny edge detection using the computed median
    # lower = int(max(0, (1.0 - 0.33) * v))
    # upper = int(min(255, (1.0 - 0.33) * v))
    #
    # processedImage = cv2.Canny(processedImage, lower,upper, 3)#cv2.Canny(processedImage, 40,170, 3)  # cv2.Canny(processedImage, 55, 60,3)#
    # if showProcess: showImage(processedImage, "Canny Iris Image")

    objCircles = cv2.HoughCircles(processedImage, cv2.HOUGH_GRADIENT,2, center[0] / 2, 30, 151)#change on 2 works on all initial

    if objCircles is None:
        print "segunda tentativa da pupila"
        processedImage = cv2.bilateralFilter(eyeImage, 30, 50, 100, 25)
        if showProcess: showImage(processedImage, "Bilateral Filtered Iris Image")
        objCircles = cv2.HoughCircles(processedImage, cv2.HOUGH_GRADIENT, 2, center[0] / 2, 30,151)

    if objCircles is None:
        print "terceira tentativa da pupila"
        processedImage = cv2.medianBlur(eyeImage, 11)#11
        if showProcess: showImage(processedImage, "Median Blurred Iris Image")
        objCircles = cv2.HoughCircles(processedImage, cv2.HOUGH_GRADIENT,2, center[0] / 2, 30, 151)#change on 2 works on all initial

    if objCircles is None:
        print "quarta tentativa da pupila"
        if showProcess: showImage(eyeImage, "Original Iris Image")
        objCircles = cv2.HoughCircles(eyeImage, cv2.HOUGH_GRADIENT, 2, center[0] / 2, 200,200)  # change on 2 works on all initial

    if objCircles is None:
        raise Exception("No Circles were found")
    elif objCircles.__len__() > 0:
        circles = objCircles[0]
        if circles.__len__() > 0:
            circle = circles[0]
            if circles.__len__() > 1:
                print("found "+str(circles.__len__())+" circles")# change on V2
                copiedImage = eyeImage.copy()
                drawCirclesOnImage(copiedImage,circles,False)
                showImage(copiedImage, "Found these ones")
            return circle
    return objCircles

def __pupilCircleOnImageV3(eyeImage,showProcess=False):
    width = eyeImage.shape[1]
    height = eyeImage.shape[0]
    average = np.median(eyeImage)
    center = (width / 2, height / 2)  # change on 2 fixing

    if showProcess : showImage(eyeImage, "Original Iris Image")

    #processedImage = cv2.medianBlur(eyeImage, 11)
    kernel = np.ones((20, 20), np.uint8)
    #kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    processedImage = cv2.dilate(eyeImage,kernel,1)
    #processedImage = cv2.erode(processedImage,kernel,1)
    processedImage = cv2.morphologyEx(eyeImage, cv2.MORPH_CLOSE, kernel)
    #processedImage = cv2.morphologyEx(processedImage, cv2.MORPH_GRADIENT, kernel)
    if showProcess: showImage(processedImage, "preprocessed binary Image")

    processedImage = cv2.Canny(processedImage, 150, 150, 30)
    if showProcess:  showImage(processedImage, "After Apply Canny")


    objCircles = cv2.HoughCircles(processedImage, cv2.HOUGH_GRADIENT, 2, width, 150, 60,1,5)

    if objCircles is None:
        raise Exception("No Circles were found")
    elif objCircles.__len__() > 0:
        circles = objCircles[0]
        if circles.__len__() > 0:
            circle = circles[0]
            if circles.__len__() > 1:
                print("found "+str(circles.__len__())+" circles")# change on V2
                copiedImage = eyeImage.copy()
                drawCirclesOnImage(copiedImage,circles,False)
                showImage(copiedImage, "Found these ones")
            return circle
    return objCircles


#this is for picamera
def __pupilCircleOnImageRaspCam(eyeImage,showProcess=False):
    width = eyeImage.shape[1]
    height = eyeImage.shape[0]
    average = np.median(eyeImage)
    center = (width / 2, height / 2)  # change on 2 fixing

    if showProcess : showImage(eyeImage, "Original Iris Image")

    print "primeira tentativa da pupila"
    #processedImage = cv2.Canny(eyeImage, 150, 50, 3)
    #if showProcess:  showImage(processedImage, "After Apply Canny")

    preprocessedImage = cv2.inRange(eyeImage,0,average+average*0.3)
    if showProcess: showImage(preprocessedImage, "preprocessed binary Image")
    processedImage = eyeImage*(preprocessedImage/255)

    if showProcess: showImage(processedImage, "preprocessed Image")

    processedImage = cv2.medianBlur(processedImage, 11)

    #processedImage = cv2.bilateralFilter(eyeImage, 30, 10, 100, 25)
    #processedImage = cv2.GaussianBlur(eyeImage, (9,9), 3, 3)  # change on 1_5

    #processedImage = cv2.medianBlur(eyeImage,11)
    #processedImage = cv2.bilateralFilter(processedImage, 30, 10, 100, 25)

    if showProcess: showImage(processedImage, "Median Blurred Iris Image")
    # processedImage = cv2.Canny(processedImage, 50, 70, 3)
    # if showProcess:  showImage(processedImage, "After Apply Canny")
    # objCircles = cv2.HoughCircles(processedImage, cv2.HOUGH_GRADIENT,2, center[0] / 2, 30, 151)#change on 2 works on all initial
    #objCircles = cv2.HoughCircles(processedImage, cv2.HOUGH_GRADIENT, 2, center[0] / 2, 100, 127, 1,10)
    #objCircles = cv2.HoughCircles(processedImage, cv2.HOUGH_GRADIENT, 2, center[0] / 2, 100, 9, 1,5)
    #objCircles = cv2.HoughCircles(processedImage, cv2.HOUGH_GRADIENT, 2, width, 100, 9, 1,5)

    #objCircles = cv2.HoughCircles(processedImage, cv2.HOUGH_GRADIENT, 2, width, 100, 100, 1,5)
    #objCircles = cv2.HoughCircles(processedImage, cv2.HOUGH_GRADIENT, 2, width, 100, 60, 1,5)
    objCircles = cv2.HoughCircles(processedImage, cv2.HOUGH_GRADIENT, 2, width, 150, 60,1,5)

    if objCircles is None:
        print "segunda tentativa da pupila"
        #processedImage = cv2.bilateralFilter(eyeImage, 30, 50, 100, 25)
        processedImage = cv2.bilateralFilter(eyeImage, 30, 10, 100, 25)
        if showProcess: showImage(processedImage, "Bilateral Filtered Iris Image")
        objCircles = cv2.HoughCircles(processedImage, cv2.HOUGH_GRADIENT, 2, width, 100, 60, 1, 5)

    if objCircles is None:
        print "terceira tentativa da pupila"
        baseKSize = 9
        blurKSize = (baseKSize, baseKSize)

        processedImage = cv2.GaussianBlur(eyeImage, blurKSize, 3, 3)  # change on 1_5

        if showProcess: showImage(processedImage, "Gaussian Blurred Iris Image")

        objCircles = cv2.HoughCircles(processedImage, cv2.HOUGH_GRADIENT, 2, center[0] / 2, 30,
                                      151)  # change on 2 works on all initial
    if objCircles is None:
        print "quarta tentativa da pupila"
        if showProcess: showImage(eyeImage, "Original Iris Image")
        objCircles = cv2.HoughCircles(eyeImage, cv2.HOUGH_GRADIENT, 2, center[0] / 2, 200,200)  # change on 2 works on all initial

    if objCircles is None:
        raise Exception("No Circles were found")
    elif objCircles.__len__() > 0:
        circles = objCircles[0]
        if circles.__len__() > 0:
            circle = circles[0]
            if circles.__len__() > 1:
                print("found "+str(circles.__len__())+" circles")# change on V2
                copiedImage = eyeImage.copy()
                drawCirclesOnImage(copiedImage,circles,False)
                showImage(copiedImage, "Found these ones")
            return circle
    return objCircles




#The image must be on gray scale
#tenta encontrar a linha formada pelas palpebras
def __eyelidsLines(eyeImage,showProcess):
    cannyImage = cv2.Canny(eyeImage,  50, 70, 3)
    if showProcess :  showImage(cannyImage,"After Apply Canny")

    lines = cv2.HoughLines(cannyImage,1,np.pi/180,1)
    if lines is None:
        raise Exception("No Lines of eyelids where found")
    print   "encontrou" + str(lines.__len__()) + " linhas"
    return lines




#-------------


#Finds the pupil on a image and draws a circle on a image presenting the pupil
def tryToShowPupil(path):
    eyeImage = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    try:
        pupilCircle = __pupilCircleOnImageV2(eyeImage, True)
        drawCirclesOnImage(eyeImage,[pupilCircle])
        showImage(eyeImage,"Circles found on Iris Image")
    except Exception, e:
        print e


def showEyeLidsOnImageAtPath(path):
    eyeImage = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    showImage(eyeImage,"Original Image")
    try:
        lines = __eyelidsLines(eyeImage, True)
        drawLinesOnImage(eyeImage,lines)
        showImage(eyeImage, "Detected Lines of eyelids")
    except Exception, e:
        print e

def segmentIrisOnImage(eyeImage):

    copyImage = cv2.cvtColor(eyeImage, cv2.COLOR_BGR2GRAY)
    #cv2.cvtColor(eyeImage,cv2.COLOR_BAYER_BG2GRAY)#eyeImage.copy()
    try:
        pupilCircle = __pupilCircleOnImageV2(copyImage,True)

        irisCircle = __irisCircleOnImageV1(copyImage,pupilCircle,True)
        drawCirclesOnImage(copyImage,[irisCircle])
        showImage(copyImage,"Circles for Iris found on Iris Image")


    except Exception, e:
        print e

#tutorial = http://www.peterkovesi.com/matlabfns/PhaseCongruency/Docs/convexpl.html
def __2DLogGaborFilter(lins,cols):
    #radius matrix
    #populate the radius matrix
    x = -(cols/2.0)
    y = -(lins/2.0)
    radius = np.zeros((lins, cols))
    for lin in range(0,lins):
        yLin = (y + lin)/lins
        line = np.zeros(cols)
        for col in range(0,cols):
            xCol = (x + col)/cols
            line[col] = math.sqrt(((xCol)**2 + (yLin)**2))#math.sqrt((((x + col)/cols)**2 + ((y + lin)/lins)**2)/2.0)
        radius[lin] = line
    radius[lins/2][cols/2] = 1
    #return radius


    ################################# radial part of filter
    waveLenght = 5.0#10.0# at least 2 #######
    f0 = 1.0/waveLenght
    sigmaOnf = 0.55#0.75 ########
    gaborRadial = np.zeros((lins, cols))
    for lin in range(0,lins):
        lineLog = np.zeros(cols)
        for col in range(0,cols):
            f = radius[lin][col]
            radialPart = math.exp(-((math.log10(f / f0)) ** 2) / (2 * (math.log10(sigmaOnf)) ** 2))
            lineLog[col] = radialPart
        gaborRadial[lin] = lineLog
    gaborRadial[lins/2][cols/2] = 0
    #return gaborRadial

    #new = cv2.normalize(gaborRadial,0,1,cv2.NORM_MINMAX)
    #showImage(new,"read")

    ################################## angular part of filter
    spread = np.zeros((lins, cols))
    thetaSigma = 1.5 ######
    for lin in range(0,lins):
        yLin = (y + lin)/lins
        spreadLine = np.zeros(cols)
        for col in range(0,cols):
            xCol = (x + col)/cols
            theta = math.atan2(-yLin,xCol)
            sinTheta = math.sin(theta)
            cosTheta = math.cos(theta)

            angl = col*math.pi/180
            ds = sinTheta*math.cos(angl) - cosTheta*math.sin(angl)
            dc = cosTheta*math.cos(angl) + sinTheta*math.sin(angl)
            dTheta = abs(math.atan2(ds,dc))

            anglePart = math.exp(-(dTheta**2)/(2*(thetaSigma)**2))
            spreadLine[col] = anglePart
        spread[lin] = spreadLine

    #return spread

    filter = spread*gaborRadial
    return filter

#http://docs.opencv.org/3.1.0/de/dbc/tutorial_py_fourier_transform.html
#using numpy
def __NP_fourierTransformOf(image,showProcess=False):
    showImage(image,"Image")
    f = np.fft.fft2(image)
    fshift = np.fft.fftshift(f)
    magnitude_spectrum = 20 * np.log(np.abs(fshift))
    if showProcess : showImage(magnitude_spectrum.astype(np.uint8), "Fourier transform")
    return fshift

#using cv2
#teorically faster
def __CV2_fourierTransformOf(image,showProcess=False):
    dft = cv2.dft(np.float32(image), flags=cv2.DFT_COMPLEX_OUTPUT)
    dft_shift = np.fft.fftshift(dft)
    magnitude_spectrum = 20 * np.log(cv2.magnitude(dft_shift[:, :, 0], dft_shift[:, :, 1]))
    if showProcess : showImage(magnitude_spectrum.astype(np.uint8), "Fourier transform")
    return dft_shift

def __CV2_invertFourierTransformOf(data):
    f_ishift = np.fft.ifftshift(data)
    img_back = cv2.idft(f_ishift)
    img_back = cv2.magnitude(img_back[:, :, 0], img_back[:, :, 1])
    return img_back

def __NP_invertFourierTransformOf(data):
    f_ishift = np.fft.ifftshift(data)
    img_back = np.fft.ifft2(f_ishift)
    img_back = np.abs(img_back)
    return img_back

#this method fixes the image to best size for improve performance of fourier transform
def __fixImgToFTBestSize(image):
    # get best size
    rows = image.shape[0]
    columns = image.shape[1]
    nrows = cv2.getOptimalDFTSize(rows)
    ncols = cv2.getOptimalDFTSize(columns)
    right = ncols - columns
    bottom = nrows - rows
    nimg = cv2.copyMakeBorder(image, 0, bottom, 0, right, cv2.BORDER_CONSTANT, value=0)
    return nimg


def segmentIrisOnImageAtPath(path):
    # type: (object) -> object

    eyeImage = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    copyImage = eyeImage.copy()
    try:
        pupilCircle = __pupilCircleOnImageV2(copyImage,True)
        irisCircle = __irisCircleOnImageV1(copyImage,pupilCircle,True)
        #image = __extractIrisData(eyeImage,pupilCircle,irisCircle)
        #showImage(image,"test")

        #pupilCircle = __pupilCircleOnImageRaspCam(copyImage,True)
        #irisCircle = __irisCircleOnImageRaspCam(copyImage,pupilCircle,True)

        drawCirclesOnImage(copyImage,[irisCircle])
        showImage(copyImage,"Circles for Iris found on Iris Image")

        #irisData = __normalizeIrisRegion(eyeImage, pupilCircle, irisCircle, 6)
        #showImage(irisData, "Normalized iris data")
        irisData = __RSM_NormIrisRegion(eyeImage, pupilCircle, irisCircle,40,3)
        showImage(irisData, "Rubber Sheet Model Normalized iris data")

        #irisCode = __2DLogGaborFilter(irisData.shape[0],irisData.shape[1])*irisData

        #irisCode = __codificateIrisData(irisData)

        #showImage(irisCode.astype(np.uint8), "Codificated Iris data")

    except Exception, e:
        print e

def fourierTransform(imagePath):
    image = cv2.imread(imagePath,cv2.IMREAD_GRAYSCALE)
    #nimage = __fixImgToFTBestSize(image)
    #showImage(nimage,"resized image")
    imgFT = __CV2_fourierTransformOf(image)
    #imgFT = __NP_fourierTransformOf(image)

    rows = imgFT.shape[0]
    cols = imgFT.shape[1]

    #gFilter = __2DLogGaborFilter(rows,cols)

    #filtered = imgFT*gFilter

    img = __CV2_invertFourierTransformOf(imgFT)
    #img = __NP_invertFourierTransformOf(imgFT)
    #showImage(img.astype(np.uint8),"After Filter")
    showImage(img,"After Filter")









