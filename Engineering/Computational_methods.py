# 1.0 Recursive implementation of Newton's Polynomials and implementation of Lagrange polynomials interpolation technique

# a recursive function that outputs all the necessary coefficients
def recursiveNewton(x, y):
    if len(x) == 1:
        return y[0] # output f(x0)
    elif len(x) == 2:
        return (y[1] - y[0])/(x[1] - x[0]) # return first difference (f(x1) - f(x0))/(x1-x0)
    else:
        # return recursive call on smaller part of the dataset
        return (recursiveNewton(x[1:], y[1:]) - recursiveNewton(x[:-1], y[:-1]))/(x[len(x) - 1] - x[0])

def polynomial(x):
    poly = 0
    for i in range(len(P)):
        coefficient = recursiveNewton(T[0:i+1], P[0:i+1])
        order = 1
        for j in range(i):
            order = order * (x - T[j])
        poly += coefficient * (order)
    
    return poly

# Lagrange interpolating polynomials
def LagrangePoly(n, x, T, P):
    f = 0
    for i in range(n):
        Li = 1
        for j in range(n):
            if j != i:
                Li = Li * (x - T[j])/(T[i] - T[j])
        f += Li * P[i]
    
    return f

# 1a: Applying the above functions by performing interpolation on a data set
T = np.array([200, 220, 240, 260, 280, 300, 320, 340, 360, 380, 400])
P = np.array([1522.6, 1559.3, 1852.8, 2156.4, 2447.2, 2425.1, 2753.2, 2683.9, 2900.1, 3230.1, 3382.0])
x = 230

T_range = np.arange(200, 400, 0.01)

fig, ax1 = plt.subplots(1, 1, figsize = (7,4))
ax1.scatter(T, P)
ax1.plot(T_range, polynomial(T_range), 'k', label="Newton polynomial")
ax1.plot(T_range, LagrangePoly(len(T), T_range, T, P), 'k', label="Lagrange polynomial")
ax1.set_title("Newton's Interpolating Polynomials")
ax1.set_xlabel('T (K)')
ax1.set_ylabel('P (Pa)')
ax1.legend()

# 2. Difference approximations
def df_forward_order1(x, h):
    fx_one = f(x + h)
    return (fx_one - f(x)) / h

def df_forward_order2(x, h):
    fx_one = f(x + h)
    fx_two = f(x + 2*h)
    return (-fx_two + 4*fx_one - 3*f(x)) / (2 * h)

def df_backward_order1(x, h):
    fx_minus_one = f(x - h)
    return (f(x) - fx_minus_one) / h

def df_backward_order2(x, h):
    fx_minus_one = f(x - h)
    fx_minus_two = f(x - 2*h)
    return (3*f(x) - 4*fx_minus_one + fx_minus_two) / (2 * h)

h = 0.5
fig, (ax1, ax2) = plt.subplots(1, 2, figsize = (9,4))
fig.suptitle('First order and second order differences vs h')
# plotting first order differences together
ax1.plot(hs, df_forward_order1(x, hs), 'k', label="Forward order 1")
ax1.plot(hs, df_centered_order1(x, hs), label="Centered order 1")
ax1.plot(hs, df_backward_order1(x, hs), label="Backward order 1")
ax1.hlines(actual_at_2, 0, 0.5, 'r', label ="True value", linestyle='--')
ax1.set_xlabel('h')
ax1.set_ylabel('Approximation')
ax1.legend()
# plotting second order differences together
ax2.plot(hs, df_forward_order2(x, hs), 'k', label="Forward order 2")
ax2.plot(hs, df_centered_order2(x, hs), label="Centered order 2") # error is of O(h^4)
ax2.plot(hs, df_backward_order2(x, hs), label="Backward order 2")
ax2.hlines(actual_at_2, 0, 0.5, 'r', label ="True value", linestyle='--')
ax2.set_xlabel('h')
ax2.legend()

# plotting first-order centered difference against the second-order forward and backward difference approximations
fig, (ax) = plt.subplots(figsize = (9,4))
fig.suptitle('First order centered difference and second order differences vs h')
ax.plot(hs, df_centered_order1(x, hs), label="Centered order 1")
ax.plot(hs, df_forward_order2(x, hs), 'k', label="Forward order 2")
ax.plot(hs, df_backward_order2(x, hs), label="Backward order 2")
ax.hlines(actual_at_2, 0, 0.5, 'r', label ="True value", linestyle='--')

ax.set_xlabel('h')
ax.set_ylabel('Approximation')
ax.legend()

# Part d
hs = np.arange(0.01, 0.5, 0.01)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize = (12,5))
fig.suptitle('Absolute errors (left) and relative errors (right) vs h')
# plot all absolute errors
ax1.plot(hs, np.abs(df(x) - df_forward_order1(x, hs)), 'k', label="Forward order 1 error")
ax1.plot(hs, np.abs(df(x) - df_centered_order1(x, hs)), label="Centered order 1 error")
ax1.plot(hs, np.abs(df(x) - df_backward_order1(x, hs)), label="Backward order 1 error")
ax1.plot(hs, np.abs(df(x) - df_forward_order2(x, hs)), label="Forward order 2 error")
ax1.plot(hs, np.abs(df(x) - df_centered_order2(x, hs)), label="Centered order 2 error")
ax1.plot(hs, np.abs(df(x) - df_backward_order2(x, hs)), label="Backward order 2 error")
ax1.set_xlabel('h')
ax1.set_ylabel('Error')
ax1.legend()
# plot all relative errors
ax2.plot(hs, np.abs((df_forward_order1(x, hs)- df(x))/df(x)), 'k', label="Forward order 1 error")
ax2.plot(hs, np.abs((df_centered_order1(x, hs) - df(x))/df(x)), label="Centered order 1 error")
ax2.plot(hs, np.abs((df_backward_order1(x, hs) - df(x))/df(x)), label="Backward order 1 error")
ax2.plot(hs, np.abs((df_forward_order2(x, hs) - df(x))/df(x)), label="Forward order 2 error")
ax2.plot(hs, np.abs((df_centered_order2(x, hs) - df(x))/df(x)), label="Centered order 2 error")
ax2.plot(hs, np.abs((df_backward_order2(x, hs) - df(x))/df(x)), label="Backward order 2 error")
ax2.legend()
ax2.set_xlabel('h')
ax2.legend()

# Electric field contour and vector
def E(x,y):
    x_vec = (x**(3)-4*x**(2)+2*x**(2)*y)
    y_vec = (2*y**(3) + 2*y**(2) + 1.5*y)
    return (x_vec, y_vec)
    
def E_magnitude(x_vec, y_vec):
    return (x_vec**2 + y_vec**2)**(1/2)

# Part a
x = np.linspace(-5, 6, 25)
y = np.linspace(-5, 6, 25)

X, Y = np.meshgrid(x, y)
electric_x, electric_y = E(X,Y)
E_mag = E_magnitude(electric_x, electric_y)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize = (14,5))
# Plot eletric field magnitude
cont = ax1.contourf(X, Y, E_mag, 20, cmap='coolwarm')
cbar = plt.colorbar(cont, ax=ax1, label='|E| (nV/um)')

ax1.set_title("Electric Field Magnitude")
ax1.set_xlabel('x (um)')
ax1.set_ylabel('y (um)')

# Plot electric vector field
ax2.quiver(X, Y, electric_x, electric_y)
ax2.set_title("Electric Vector Field")
ax2.set_xlabel('x (um)')
ax2.set_ylabel('y (um)')

# part b
def df_centered_order1(x, y, h):
    dEx_one = (E(x + h, y)[0] - E(x - h, y)[0]) / (2*h)
    dEy_one = (E(x, y + h)[1] - E(x, y - h)[1]) / (2*h)
    return dEx_one + dEy_one

def df_centered_order2(x, y, h, e):
    dEx = (-E(x + 2*h, y)[0] + 8*E(x+h,y)[0] - 8*E(x-h,y)[0] + E(x-2*h, y)[0]) / (12 * h)
    dEy = (-E(x, y + 2*h)[1] + 8*E(x,y+h)[1] - 8*E(x,y-h)[1] + E(x, y-2*h)[1]) / (12 * h)
    return (dEx + dEy) * e

e = 3.9
h = 0.5
free_charge = df_centered_order2(X, Y, h, e)

fig, ax = plt.subplots(1, 1, figsize = (8,5))
cont = ax.contourf(X, Y, free_charge, 15, cmap='coolwarm')
cbar = plt.colorbar(cont, label='|p| (C/um^3)')

ax.set_title("Free charge density with e = 3.9")
ax.set_xlabel('x (um)')
ax.set_ylabel('y (um)')
