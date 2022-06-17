import os
import re
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as clrs
from sklearn.cluster import KMeans

mypath = "./working/"
resultpath = "./processed/"
N_clusters = 25

(_, _, filenames) = next(os.walk(mypath))
print(filenames)

#print("reading files")

pattern_frame = re.compile(r"^(.*?G0.*?)(G0.*)(M5.*?)$",re.DOTALL)
pattern_lines = re.compile(r"G0 ",re.DOTALL)
pattern_coords = re.compile(r"X(\d*\.?\d*) Y(\d*\.?\d*).*X(\d*\.?\d*) Y(\d*\.?\d*)", re.DOTALL)
for filename in filenames:
    x_coords = []
    y_coords = []
    s_x_coords = []
    s_y_coords = []
    e_x_coords = []
    e_y_coords = []
    xmax = 0
    ymax = 0
    full_filename = mypath+filename
    f=open(full_filename, "r", encoding="utf8")
    if f.mode =='r':
        contents = f.read()
        f.close()
        new_filename = resultpath + re.sub(".nc","-o.nc",filename)
        f2 = open(new_filename, "w")
        match_frame = pattern_frame.search(contents)
        (intro, lines, outro) = match_frame.group(1,2,3)
        f2.write(intro)
#        print(intro)
#        print(outro)
        line_list = pattern_lines.split(lines)
        for i in range(len(line_list)-1,-1,-1):
            if not line_list[i]:
                line_list.pop(i)
        for i in range(0,len(line_list)):
            match_coords = pattern_coords.search(line_list[i])
            if match_coords:
                coords = map(float,match_coords.group(1,2,3,4))
                (X1,Y1,X2,Y2) = coords
                s_x_coords.append(X1)
                s_y_coords.append(Y1)
                e_x_coords.append(X2)
                e_y_coords.append(Y2)
                CX = (X1+X2)/2
                CY = (Y1+Y2)/2
                x_coords.append(CX)
                y_coords.append(CY)
                if max(X1,X2)> xmax:
                    xmax = max(X1,X2)
                if max(Y1,Y2)>ymax:
                    ymax = max(Y1,Y2)
            else:
                print("this line didn't match the expected pattern:")
                print(line_list[i])
                break
        df = pd.DataFrame({
                'x': x_coords,
                'y': y_coords
                })
        kmeans = KMeans(n_clusters=N_clusters)
        kmeans.fit(df)
        labels = kmeans.predict(df)
        centroids = kmeans.cluster_centers_

        #print(labels)
        #print(centroids)
        current_coords = [0,0]
        new_coords = [0,0]
        label_order = []
        labels_unordered = list(range(0,N_clusters))
        cluster_start = []
        cluster_end = []
        for label in labels_unordered:
            start_coords = None
            end_coords = None
            for i in range(0,len(line_list)):
                if labels[i] == label:
                    if start_coords == None:
                        start_coords = [s_x_coords[i],s_y_coords[i]]
                    end_coords = [e_x_coords[i],e_y_coords[i]]
            cluster_start.append(start_coords)
            cluster_end.append(end_coords)
        while labels_unordered:
            closest = None
            min_dist = None
            for label in labels_unordered:
                label_coords = cluster_start[label]
                this_dist = (current_coords[0]-label_coords[0])**2 + (current_coords[1]-label_coords[1])**2
                if (closest == None) or (this_dist<min_dist):
                    closest = label
                    min_dist = this_dist
                    new_coords = cluster_end[label]
            label_order.append(closest)
            labels_unordered.remove(closest)
            current_coords = new_coords
        
        for label in label_order:
            for i in range(0,len(line_list)):
                if labels[i] == label:
                    f2.write("G0 "+ line_list[i])
                
        f2.write(outro)
        f2.close()
        
        fig = plt.figure(figsize=(5, 5))
        colmap = [ clrs.hsv_to_rgb([(8*i/N_clusters)%1,1,1]) for i in range(0,N_clusters)]
        #print(colmap)
        colors = [ colmap[labels[i]] for i in range(0,len(labels))]
        #colors = map(lambda x: colmap[x+1], labels)

        plt.scatter(df['x'], df['y'], c=colors, alpha=0.5, edgecolor='k')
        for idx, centroid in enumerate(centroids):
            plt.scatter(*centroid, color=colmap[idx])
        plt.xlim(0, xmax)
        plt.ylim(0, ymax)
        plt.show()
