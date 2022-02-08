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
