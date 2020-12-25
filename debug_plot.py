
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
#mpl.use('tkagg')


def plot_spline(spline):
	left = spline.knots[0]
	right = spline.knots[-1]
	o = 0# 0.02 * (right-left)
	xx = np.linspace(left-o, right+o, 1000)
	yy = [spline[x] for x in xx]
	
	plt.plot(xx,yy)
	#plt.plot([left, right],[spline[left],spline[right]],'o')


def plot_spline_accel(spline):
    ax1 = plt.subplot(3,1,3)
    plot_spline(spline.integrate().integrate())
    plt.title('Position')
    plt.xlabel('time (s)')
    plt.ylabel('mm')

    ax2 = plt.subplot(3,1,2, sharex = ax1)
    plot_spline(spline.integrate())
    plt.setp(ax2.get_xticklabels(), visible=False)
    plt.title('Velocity')
    plt.ylabel('mm/s')

    ax3 = plt.subplot(3,1,1, sharex = ax1)
    plot_spline(spline)
    plt.setp(ax3.get_xticklabels(), visible=False)
    plt.title('Acceleration')
    plt.ylabel('mm/s$^2$')
    plt.show()

def plot_discretized(curves):    
    ax1 = plt.subplot(len(curves)-1,1,len(curves)-1)
    for i in range(len(curves)-1):
        if i > 0:
            ax = plt.subplot(len(curves)-1,1,len(curves)-i-1, sharex = ax1)
            plt.setp(ax.get_xticklabels(), visible=False)
        else:
            ax = ax1
        plt.plot(curves[-1],curves[i])
        plt.plot(curves[-1],curves[i],'o')
    plt.show()
    