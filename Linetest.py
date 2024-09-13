import cv2
import numpy as np
import matplotlib
from matplotlib.pyplot import imshow
from matplotlib import pyplot as plt
import os

###################################################################################################################################

# def pause():
    # programPause = input("Press the <ENTER> key to continue...")


url = 'http://192.168.0.2:5000/video_feed'
cap = cv2.VideoCapture(url)
#cap.read()
ret, frame = cap.read()
#cv2.imshow("title",frame)
# white color mask
img = cv2.imread('beigeSquare.jpg')
#cv2.imshow("original",img)
image = cv2.cvtColor(img,cv2.COLOR_BGR2HLS)
lower = np.uint8([0, 200, 0])
upper = np.uint8([255, 255, 255])
white_mask = cv2.inRange(image, lower, upper)
# yellow color mask
lower = np.uint8([10, 0,   100])
upper = np.uint8([40, 255, 255])
yellow_mask = cv2.inRange(image, lower, upper)
# combine the mask
mask = cv2.bitwise_or(white_mask, yellow_mask)
result = img.copy()
gray_result = frame.copy()
#cv2.imshow("mask",mask)
#pause()
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
gray_cap = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

edges = cv2.Canny(mask, 50, 200)
edges2 = cv2.Canny(gray, 100, 300)
gray_edges = cv2.Canny(gray_cap, 100, 300)
#cv2.imshow("edges",edges)
#cv2.imshow("edges2",edges2)
lines = cv2.HoughLinesP(edges,1,np.pi/180,40,minLineLength=30,maxLineGap=30)
#gray_lines = cv2.HoughLinesP(gray_edges,1,np.pi/180,40,minLineLength=30,maxLineGap=30)

rho = 1  # distance resolution in pixels of the Hough grid
theta = np.pi / 180  # angular resolution in radians of the Hough grid
threshold = 15  # minimum number of votes (intersections in Hough grid cell)
min_line_length = 5  # minimum number of pixels making up a line
max_line_gap = 20  # maximum gap in pixels between connectable line segments
#line_image = np.copy(img) * 0  
line_image = img.copy()
gray_line_image = frame.copy()

# Run Hough on edge detected image
# Output "lines" is an array containing endpoints of detected line segments
lines2 = cv2.HoughLinesP(edges2, rho, theta, threshold, np.array([]), min_line_length, max_line_gap)
gray_lines = cv2.HoughLinesP(gray_edges, rho, theta, threshold, np.array([]), min_line_length, max_line_gap)

for line in lines2:
    for x1,y1,x2,y2 in line:
        cv2.line(line_image,(x1,y1),(x2,y2),(255,0,0),1)
        #print(x1,y1,x2,y2)

for line2 in gray_lines:
    for g_x1,g_y1,g_x2,g_y2 in line2:
        cv2.line(gray_line_image,(g_x1,g_y1),(g_x2,g_y2),(255,0,0),1)

# Draw the lines on the  image
#lines_edges = cv2.addWeighted(img, 1, line_image, 1, 0)
#cv2.imshow('Line_Edges',lines_edges)
cv2.imshow('Line_Edges',line_image)
cv2.imshow('Gray Line Edges',gray_line_image)

i = 0
for x1,y1,x2,y2 in lines[0]:
    i+=1
    cv2.line(result,(x1,y1),(x2,y2),(255,0,0),1)
print (i)

#cv2.imshow("res",result)
cv2.waitKey(0)
cap.release()
cv2.destroyAllWindows()
print("Camera disabled and all output windows closed...")


#######################################################################################################################################

# img = cv2.imread('beigeSquare.jpg')
# gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)

# kernel_size = 5
# blur_gray = cv2.GaussianBlur(gray,(kernel_size, kernel_size),0)

# cv2.imshow('blur_gray',blur_gray)

# low_threshold = 20
# high_threshold = 200
# edges = cv2.Canny(blur_gray, low_threshold, high_threshold)

# rho = 1  # distance resolution in pixels of the Hough grid
# theta = np.pi / 180  # angular resolution in radians of the Hough grid
# threshold = 15  # minimum number of votes (intersections in Hough grid cell)
# min_line_length = 50  # minimum number of pixels making up a line
# max_line_gap = 20  # maximum gap in pixels between connectable line segments
# line_image = np.copy(img) * 0  # creating a blank to draw lines on

# # Run Hough on edge detected image
# # Output "lines" is an array containing endpoints of detected line segments
# lines = cv2.HoughLinesP(edges, rho, theta, threshold, np.array([]),
                    # min_line_length, max_line_gap)

# for line in lines:
    # for x1,y1,x2,y2 in line:
        # cv2.line(line_image,(x1,y1),(x2,y2),(255,0,0),5)


# # Draw the lines on the  image
# lines_edges = cv2.addWeighted(img, 1, line_image, 1, 0)
# cv2.imshow('title',lines_edges)
# cv2.waitKey(0)

#####################################################################################################################################

#import cv2
#import numpy as np
#import matplotlib
#from matplotlib.pyplot import imshow
#from matplotlib import pyplot as plt
#import os











