from scipy.optimize import minimize
from scipy.integrate import odeint
import numpy as np
import matplotlib.pyplot as plt
# from time import time


class UHandle:
    def __init__(self):
        self.dt = None
        self.u = None
        self.sp = None
        self.t0 = 0.0

    def set_u(self, u):
        self.u = u

    def set_sp(self, sp):
        self.sp = sp

    def get(self, t):
        tb = t - self.t0
        n = min(max(0, int(tb / self.dt)) + 1, len(self.u) - 1)
        return self.u[n]

    def get_sp(self, t):
        tb = t - self.t0
        n = min(max(0, int(tb / self.dt)), len(self.sp) - 1)
        return self.sp[n]

    def update(self, t, u):
        tb = t - self.t0
        n = max(0, int(tb / self.dt)) + 1
        if n <= len(self.u) - 1:
            self.u[n] = u
        else:
            pass
            # self.u[-1] = self.u[-1]


class Model(object):
    def __init__(self):
        super(Model, self).__init__()

        self.model_type = 'FOPDT'
        self.model = None
        self.dt = None
        self.sim_time = None
        self.n_sim = None
        self.t = None

        # Transfer Function
        self.k_p = None
        self.tau_p = None
        self.theta_p = None
        self.zeta = None
        self.U = UHandle()


class PID(object):
    def __init__(self):
        super(PID, self).__init__()

        self.setpoint = None
        self.dt = None
        self.DT = None

        self.k_c = None
        self.tau_i = None
        self.tau_d = None

        self.kc_lb = None
        self.kc_ub = None
        self.taui_lb = None
        self.taui_ub = None
        self.taud_lb = None
        self.taud_ub = None

        self.error = 0
        self.integral_error = 0
        self.derivative_error = 0
        self.error_last = 0

        self.saturation_min = None
        self.saturation_max = None

        self.delta_max = None

        self.op_last = 0
        self.pv_last = 0

        self.derivative_type = 'pv'

    def pid(self, pv, setpoint, k_c, tau_i, tau_d):
        self.error = setpoint - pv
        self.integral_error += self.error * self.dt
        self.derivative_error = (pv - self.pv_last) / self.dt
        self.error_last = self.error

        op = k_c * self.error \
             + k_c / tau_i * self.integral_error \
             - k_c * tau_d * self.derivative_error

        delta_op = op - self.op_last
        if self.saturation_max is not None:
            if delta_op.value > self.saturation_max:
                delta_op.value = self.saturation_max

        if self.saturation_min is not None:
            if delta_op < self.saturation_min:
                delta_op = self.saturation_min

        if self.delta_max is not None:
            delta_op = max(min(delta_op, self.delta_max), -self.delta_max)

        op = delta_op + self.op_last
        self.op_last = op
        self.pv_last = pv

        return op

    def set_sat_lims(self, lb, ub):
        self.saturation_max = ub
        self.saturation_min = lb

    def set_delta_max(self, delta_max):
        self.delta_max = delta_max

    # def build(self, t):


class Method(object):
    def __init__(self):
        super(Method, self).__init__()
        self.tau_c = None


class PIDTuner(Model, PID, Method):
    def __init__(self):
        super(PIDTuner, self).__init__()

    def rule_based(self, method='IMC', **kwargs):
        if method == 'IMC':
            return self.imc_calc(kwargs['mode'], kwargs['tau_c'])
        elif method == 'Cohen-Cohn':
            pass

    def imc_calc(self, mode='moderate', tau_c=None):
        if mode == 'conservative':
            tau_c = max(10.0 * self.tau_p, 80.0 * self.theta_p)
        elif mode == 'moderate':
            tau_c = max(1.0 * self.tau_p, 8.0 * self.theta_p)
        elif mode == 'aggressive':
            tau_c = max(0.1 * self.tau_p, 0.8 * self.theta_p)
        elif mode == 'manual':
            pass

        k_c = 1 / self.k_p * (self.tau_p + 0.5 * self.theta_p) / (tau_c + 0.5 * self.theta_p)
        tau_i = self.tau_p + 0.5 * self.theta_p

        tau_d = self.tau_p * self.theta_p / (2 * self.tau_p + self.theta_p)

        return k_c, tau_i, tau_d, tau_c

    def simulate(self, **args):
        if self.model_type == 'FOPDT':
            if self.sim_time is None:
                self.sim_time = 5 * self.tau_p
                self.n_sim = int(self.sim_time / self.dt)
                self.t = np.linspace(0, self.sim_time, self.n_sim + 1)

            return self._simulate_fopdt()

    def _simulate_fopdt(self):
        y_i = [0]

        y = []
        y.extend(y_i)

        t_span = np.array([0, self.dt])

        for k in range(self.n_sim):
            sp = self.U.get_sp(self.t[k])

            op = self.pid(y[k], sp, self.k_c, self.tau_i, self.tau_d)

            self.U.update(self.t[k], op)
            y_i = odeint(self.fopdt, y_i[-1], t_span, args=(self.k_p, self.tau_p, self.theta_p))
            y.extend(y_i[-1])
            t_span += self.dt
        return self.t, self.U.u, y, self.U.sp

    def fopdt(self, y, t, k_p, tau_p, theta_p):
        op_delayed = self.U.get(t - theta_p)

        dy = [0]
        # FOPDT Equation
        # tau_p*dy/dt  = kp*u(t-theta_p) - y(t)
        dy[0] = (k_p * op_delayed - y[0]) / tau_p
        return dy

    def set_sim_time(self, t_sim):
        self.sim_time = float(t_sim)
        self.n_sim = int(self.sim_time / self.dt)
        self.t = np.linspace(0, self.sim_time, self.n_sim + 1)

    def set_dt(self, dt):
        self.dt = dt
        self.U.dt = dt

    def reset_u(self):
        u = np.zeros_like(self.t)
        self.U.set_u(u)

    def reset_sp(self):
        sp = np.zeros_like(self.t)
        sp[min(5, self.n_sim):] = self.setpoint
        self.U.set_sp(sp)

    def optimization_base(self):
        if self.model_type == 'FOPDT':
            k_c0, tau_i0, tau_d0, _ = self.imc_calc(mode='moderate')
            bounds = ((self.kc_lb, self.kc_ub),
                      (self.taui_lb, self.taui_ub),
                      (self.taud_lb, self.taud_ub))
            
            k_c, tau_i, tau_d = minimize(self._optimize_fopdt, x0=(k_c0, tau_i0, tau_d0),
                                         bounds=bounds,
                                         method='SLSQP',
                                         # tol=1e-7,
                                         options={'disp': False, 'eps': 1e-4, 'maxiter': 10}).x

            self.k_c = k_c
            self.tau_i = tau_i
            self.tau_d = tau_d

            self.reset_sp()
            self.reset_u()
            self.error = 0
            self.integral_error = 0
            self.derivative_error = 0
            self.op_last = 0
            self.pv_last = 0

            t, op, pv, sp = self.simulate()
            return t, op, pv, sp

    def _optimize_fopdt(self, params):
        self.reset_sp()
        self.reset_u()
        self.error = 0
        self.integral_error = 0
        self.derivative_error = 0
        self.op_last = 0
        self.pv_last = 0

        k_c, tau_i, tau_d = params

        y_i = [0]

        y = []
        y.extend(y_i)

        t_span = np.array([0, self.dt])

        for k in range(self.n_sim):
            sp = self.U.get_sp(self.t[k])

            op = self.pid(y[k], sp, k_c=k_c, tau_i=tau_i, tau_d=tau_d)

            self.U.update(self.t[k], op)
            y_i = odeint(self.fopdt, y_i[-1], t_span, args=(self.k_p, self.tau_p, self.theta_p))
            y.extend(y_i[-1])
            t_span += self.dt

        y = np.array(y)
        e = y - self.U.sp

        obj = 0.01*sum((self.t*e) ** 2) \
            + 10*sum(e.clip(min=0))
        return obj


# pid = PIDTuner()

# pid.k_p = 1
# pid.tau_p = 30.0
# pid.theta_p = 0.0

# pid.kc_lb = 0.001
# pid.kc_ub = 100

# pid.taui_lb = 1
# pid.taui_ub = 150

# pid.taud_lb = 0
# pid.taud_ub = 0.1

# # pid.k_c, pid.tau_i, pid.tau_d, pid.tau_c = pid.rule_based(method='IMC', mode='manual', tau_c=20)

# sim_time = 400.0
# dt = 2.0
# sp0 = 1.0

# pid.setpoint = 1

# pid.set_dt(dt)
# pid.set_sim_time(sim_time)

# pid.reset_u()
# pid.reset_sp()

# pid.set_delta_max(0.5)


# t, op, pv, sp = pid.optimization_base()

# plt.subplot(2, 1, 1)
# plt.plot(t, pv)
# plt.plot(t, sp)

# plt.subplot(2, 1, 2)
# plt.step(t, op)
# plt.show()