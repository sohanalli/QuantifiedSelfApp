import matplotlib.pyplot as plt

def draw_graph(logs):
    figure = plt.figure()
    axes = figure.add_subplot(1,1,1)
    # axes.plot([1,2,3,4], [6,5,7,12])
    # axes.bar([1,2,3,4], [6,5,7,12])
    axes.bar(
        [log.timestamp for log in logs],
        [log.value for log in logs]
    )
    return figure