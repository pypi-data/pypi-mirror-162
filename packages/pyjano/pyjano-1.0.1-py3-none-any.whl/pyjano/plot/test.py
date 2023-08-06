import matplotlib.pyplot as plt
import matplotlib.animation as anim
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d import proj3d
from matplotlib.patches import FancyArrowPatch
import numpy as np


# Custom class for 3D arrows
class Arrow3D(FancyArrowPatch):
    def __init__(self, xs, ys, zs, *args, **kwargs):
        FancyArrowPatch.__init__(self, (0, 0), (0, 0), *args, **kwargs)
        self._verts3d = xs, ys, zs

    def draw(self, renderer):
        xs3d, ys3d, zs3d = self._verts3d
        xs, ys, zs = proj3d.proj_transform(xs3d, ys3d, zs3d, renderer.M)
        self.set_positions((xs[0], ys[0]), (xs[1], ys[1]))
        FancyArrowPatch.draw(self, renderer)

    def set_data(self, xs, ys, zs):
        self._verts3d = xs, ys, zs


# Constants
B = 1.0
q = -1.0
m = 1.0
beta = 0  # beta = v/c. beta = 0 is the classical limit
gamma = 1 / (1 - beta ** 2)

a = q * B / (m * gamma)
v_0 = [1.0, 0.0, 2.0]


# Equations of motion r(t)
def r(t):
    return np.array([v_0[1] / a * (1 - np.cos(a * t)) + v_0[0] / a * np.sin(a * t) - v_0[1] / a,
                     -v_0[0] / a * (1 - np.cos(a * t)) + v_0[1] / a * np.sin(a * t) + v_0[0] / a, v_0[2] * t])


# First time derivative of r(t)
def v(t):
    return 0.5 * np.array(
        [v_0[0] * np.cos(a * t) + v_0[1] * np.sin(a * t), -v_0[0] * np.sin(a * t) + v_0[1] * np.cos(a * t), v_0[2]])


# Second time derivative of r(t)
def acc(t):
    return 0.5 * np.array([-a * v_0[0] * np.sin(a * t) + a * v_0[1] * np.cos(a * t),
                           -a * v_0[0] * np.cos(a * t) - v_0[1] * a * np.sin(a * t), 0])


fig = plt.figure()
ax = Axes3D(fig)
t_range = np.linspace(0, 30, 200)
r_t = r(t_range)
v_t = v(t_range)
acc_t = acc(t_range)
ax.plot(r_t[0], r_t[1], r_t[2], linestyle=':', c='black')  # Plot the path

# Plot the arrows and customize the axes
B_arrow = Arrow3D([0, 0], [0, 0], [0, 60], arrowstyle="-|>", lw=2, mutation_scale=20, color="blue")
ax.add_artist(B_arrow)

B_arrow = Arrow3D([0, -1], [0, 0], [0, 0], linestyle='--', arrowstyle="-|>", lw=1, mutation_scale=20, color="blue")
ax.add_artist(B_arrow)

point = ax.scatter(r_t[0][0], r_t[1][0], r_t[2][0], s=100, c='red')

v_arrow = Arrow3D(r_t[0][0] + [0, v_t[0][0]], r_t[1][0] + [0, v_t[1][0]], r_t[2][0] + [0, v_t[2]], arrowstyle="-|>",
                  lw=2, mutation_scale=20, color="green")
ax.add_artist(v_arrow)

a_arrow = Arrow3D(r_t[0][0] + [0, acc_t[0][0]], r_t[1][0] + [0, acc_t[1][0]], r_t[2][0] + [0, acc_t[2]],
                  arrowstyle="-|>", lw=2, mutation_scale=20, color="brown")
ax.add_artist(a_arrow)

ax.legend([B_arrow, v_arrow, a_arrow], ['Magnetic Field', 'Velocity', 'Acceleration'])
ax.set_axis_off()

plt.show()

#
#
# # Animate the plot
# def animate(num):
#     point._offsets3d = ([r_t[0][num]], [r_t[1][num]], [r_t[2][num]])
#     v_arrow.set_data(r_t[0][num] + [0, v_t[0][num]], r_t[1][num] + [0, v_t[1][num]], r_t[2][num] + [0, v_t[2]])
#     a_arrow.set_data(r_t[0][num] + [0, acc_t[0][num]], r_t[1][num] + [0, acc_t[1][num]], r_t[2][num] + [0, acc_t[2]])
#     return point,
#
#
# # Save the video
# ani = anim.FuncAnimation(fig, animate, 200, interval=100)
#ani.save("magneticmotion.mp4", fps=25, dpi=150)