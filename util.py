#util.py by Ryan Traviss
import matplotlib.pyplot as plt, numpy as np, datetime, statistics, json

def table(data, missing_data_items=0, sort_by_likes=False, sort="asc", max_rows=100, print_latex=False,unique=False):
    """
    Produces a full table of the selected data including summary statistics.

    Parameters
    ----------
    data : list of integers
        The data being analized.
    missing_data_items : integer, optional
        The number of missing 0's. The default is 0.
    sort_by_likes : boolean, optional
        Should the table be sorted by like counts. The default is False.
    max_rows : integer, optional
        The maximum number of rows that should be displayed. The default is 100.
        
    Returns
    -------
    None.

    """
    if data == []:
        print("Error: No data to make table")
        return
    if unique:
        data_item, data_frequency = data
    else:
        data_item, data_frequency = np.unique(data, return_counts=True)
    if sort_by_likes:
        data_frequency, data_item = zip( *sorted( zip(data_frequency, data_item), reverse=True ) )
        
    print("data_item data_frequency")
    if sort == "asc":
        for i in range(min(len(data_item),max_rows)):
            print(data_item[i],data_frequency[i])
    else:   #descending order
        for i in range(len(data_item)-1,(len(data_item)-max_rows),-1):
            print(data_item[i],data_frequency[i])
    
    if missing_data_items == 0:
        print("Please enter the amount of missing data items for the table above:")
        print("Enter 0 if all the data items appear")
        missing_data_items = int(input(">>>"))
    for x in range(0,missing_data_items):
        data_frequency = np.append(data_frequency,[0])
    
    print("Total", sum(data_frequency))
    print("n",len(data_item))
    print("Mean", np.mean(data_frequency))
    print("Median", statistics.median(data_frequency))
    print("SD",statistics.pstdev(data_frequency)) #population standard deviation
    print("Range",max(data_frequency)-min(data_frequency))
    print("Note:", missing_data_items,"missing 0's were added for the purpose of calulations")
    
    if print_latex:
        print("\n","#"*20,"Latex","#"*20)
        print("""\\begin{table}[h]\n\centering\n\caption{TBC}\n\label{table:1}\n\\begin{tabular}{ |c|c| } \n \hline TBC & TBC""")
        if sort == "asc":
            for i in range(min(len(data_item),max_rows)):
                print(data_item[i],"&",data_frequency[i],"\\\\",end="")
        else:   #descending order
            for i in range(len(data_item)-1,(len(data_item)-max_rows),-1):
                print(data_item[i],"&",data_frequency[i],"\\\\",end="")
        print("\hline Total &",sum(data_frequency),"\\\\")
        print("\hline Mean &",np.mean(data_frequency),"\\\\")
        print("\hline n &",len(data_item),"\\\\")
        print("Median &", statistics.median(data_frequency),"\\\\")
        print("SD & ",statistics.pstdev(data_frequency),"\\\\")
        print("Range & ",max(data_frequency)-min(data_frequency),"\\\\")
        print(""" \hline\n\end{tabular}\n\end{table}""")
    
def graph(time_data,date,xlabel,style = "-b",unique = False, xtick_min=0, xtick_max = 0,ylabel="Activity"):
    """
    Plots the line graph of the data with nice formatting.

    Parameters
    ----------
    time_data : tuple or list
        The data to be plotted.
    date : string
        The period the data covers to add to the title.
    xlabel : string
        Self-explanatory.
    style : string, optional
        How the graph should look(shape of crosses, line graph vs scatter ect). The default is "-b".
    unique : Boolean, optional
        If np.unique been not been done already?. The default is False.
    xtick_max : integer, optional
        What should the xticks go up to from 0 (if 0 default behaviour is used). The default is 0.

    Returns
    -------
    None.

    """
    if time_data == [] or time_data == ([],[]):
        print("Error: No data to plot a line graph")
        return
    if unique:
        time,like_counts = time_data
    else:
        time,like_counts = np.unique(time_data, return_counts=True)
        
    plt.plot(time,like_counts,style)
    if xtick_max != 0:
        plt.xticks(range(xtick_min,xtick_max))
    else:
        plt.xticks([time[x] for x in range(0,len(time),6)])
    
    plt.xlabel(xlabel)
 
    plt.title(ylabel+" per " +xlabel+ " in "+date)
    plt.ylabel(ylabel)
    
    plt.show()
    #plt.savefig("D:\ExeterMathsSchool\My Data Individual EMC\graphs\media_likes_months_"+year)

def graph_boxplot(time_data,date,xlabel, xtick_max=0):
    """
    Plots the boxplot of the data with nice formatting.

    Parameters
    ----------
    time_data : list of integers
        The data to be plotted.
    date : string
        When the data is from.
    xlabel : string
        Self-explanatory.
    xtick_max : integer, optional
        What should the xticks go up to from 0 (if 0 default behaviour is used). The default is 0.

    Returns
    -------
    None.

    """
    if time_data == []:
        print("Error: No data to make a boxplot")
        return
    plt.boxplot(time_data,vert=False)
    if xtick_max != 0:
        plt.xticks(range(0,xtick_max))
    #plt.xticks(range(min(time_data),max(time_data)))
    plt.xlabel(xlabel)
    plt.title("Activity per " +xlabel+ " in "+date)
    plt.ylabel("Activity")
    plt.yticks([])#This removes the 1 on the y-axis which is there by default
    plt.show()

def json_file_structure(json_data, tabs=0):
    """
    Prints the file structure of a JSON file that has been opened using recursion.

    Parameters
    ----------
    json_data : dictionary
        An opened JSON file eg likes_json_data.
    tabs : integer, optional
        How many tabs should be displayed. The default is 0.

    """
    if type(json_data) is dict:
        for key in json_data.keys():
            print("\t"*tabs+key)
            json_file_structure(json_data[key],tabs=tabs+1)
    elif type(json_data) is list:
        keys = []
        for i in range(len(json_data)):
            if type(json_data[i]) is dict:
                if json_data[i].keys() not in keys:
                    keys.append(json_data[i].keys())
                    
                    json_file_structure(json_data[i],tabs=tabs+1)
                    print("\t"*tabs+str(json_data[i].keys()))
            else:
                print("\t"*tabs+"["+ str(i) +"]")
                json_file_structure(json_data[i],tabs=tabs+1)
        if len(keys) > 1:
            print("\t"*tabs+str(keys))
        
    else:
        print("\t"*tabs+str(json_data).replace("\n","\\\\"))
        
def read_json(filename):
    """
    Opens the file, reads the data, closes it and turns it into a dictionary. 

    Parameters
    ----------
    filename : string
        The filename of a JSON file to be opened and read.

    Returns
    -------
    Dictionary
        The JSON data in the file as a Python dictionary.

    """
    with open(filename, "r", encoding="utf8") as f:
        return json.loads(f.read())
    
def date_to_time_period(date):
    """
    Converts part of a date to what xlabel that would be.

    Parameters
    ----------
    date : string
        eg 2020-10.

    Returns
    -------
    str
        The time period the partial date represents.

    """
    if len(date) == 0:
        return "all time"
    else:
        return date
