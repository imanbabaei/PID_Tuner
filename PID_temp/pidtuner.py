import matplotlib.pyplot as plt
import numpy as np
from gekko import GEKKO


class PIDTuner:
    def __init__(self, kp, taup, thetap):
        # Controller Parameters
        self.k_c = None
        self.tau_i = None
        self.tau_d = None

        # Model Parameters
        self.k_p = None
        self.tau_p = None
        self.theta_p = None
        
        # Solver Params
        self.sp0=1
        self.pv0=0
        self.op0=0
        self.dt0=1
    
        
    def rule_based(self, method='IMC', *args, **kwargs):
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
            # tau_c = tau_c

        k_c = 1 / self.k_p * (self.tau_p + 0.5 * self.theta_p) / (tau_c + 0.5 * self.theta_p)
        tau_i = self.tau_p + 0.5 * self.theta_p
        tau_d = self.tau_p * self.theta_p / (2 * self.tau_p + self.theta_p)

        return k_c, tau_i, tau_d

    def control_sim(self):
        k_p = self.k_p
        tau_p = self.tau_p
        theta_p = self.theta_p

        k_c = self.k_c
        tau_i = self.tau_i
        tau_d = self.tau_d
        op0 = self.op0
        pv0 = self.pv0

        m = GEKKO(remote=False)
        tf = min(4*tau_p, 25*tau_p*abs(k_c))
        dt = self.dt0/4
        n_sim = int(tf/dt)
        m.time = np.linspace(0, tf, n_sim)
        step = np.zeros_like(m.time)
        step[n_sim // 7:] = self.sp0

        pv = m.Var(value=pv0)
        op = m.Var(value=op0)
        opd = m.Var(op)
        if (theta_p/dt)>=1:
            m.delay(op, opd, int(theta_p/dt))
        else:
            m.Equation(opd == op)
        sp = m.Param(value=step)
        integ = m.Var(value=0)
        
        err = m.Intermediate(sp - pv)
        # err = m.Var(0)
        # m.Equation(err == sp - pv)
        m.Equation(integ.dt() == err)

        # PID Equation
        m.Equation(op == op0 + k_c * err + (k_c / tau_i) * integ - k_c * tau_d * pv.dt())

        # Model Equation
        m.Equation(tau_p * pv.dt() + pv == k_p * opd)

        m.options.IMODE = 4
        m.solve(disp=False)

        return pv, op, m.time

    # def tau_based_calc(self, tau):


# pid = PIDTuner()
#
# pid.k_p = -1504
# pid.tau_p = 197
# pid.theta_p = 1
# pid.k_c = -0.065
# pid.tau_i = 8
# pid.tau_d = 0
# pid.k_c, pid.tau_i, pid.tau_d = pid.imc_calc(mode='manual', tau_c=1)
#
# pv, op, t = pid.control_sim(sp0=1, pv0=0, op0=0, dt0=1)
#
# plt.subplot(2, 1, 1)
# plt.plot(t, pv.value)
#
# plt.subplot(2, 1, 2)
# plt.plot(t, op.value)
#
# plt.show()
