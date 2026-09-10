from pathlib import Path

bg_file = Path("source/background.c")
hd_bg_file = Path("include/background.h")
inp_file = Path("source/input.c")
hd_pt_file = Path("include/perturbations.h")
pt_file = Path("source/perturbations.c")

bg = bg_file.read_text().splitlines()
hd_bg = hd_bg_file.read_text().splitlines()
inp = inp_file.read_text().splitlines()
hd_pt = hd_pt_file.read_text().splitlines()
pt = pt_file.read_text().splitlines()

# --- A. Headers & Helper Functions ---
idx = [i for i, l in enumerate(hd_bg) if "short has_dcdm;" in l][0]
hd_bg.insert(idx + 1, "  short has_qrubin;")
idx2 = [i for i, l in enumerate(hd_bg) if "double Gamma_dcdm;" in l][0]
hd_bg.insert(idx2 + 1, "  double M_Q;\n  double a_t;\n  double n_qrubin;\n  double A0_qrubin;\n  double B0_qrubin;\n  double phi0_qrubin;\n  double tau_Q;\n  double Gamma0_qrubin;\n  double S0_qrubin;\n  double D0_qrubin;")
idx3 = [i for i, l in enumerate(hd_bg) if "int index_bg_rho_cdm;" in l][0]
hd_bg.insert(idx3 + 1, "  int index_bg_W_qrubin;\n  int index_bg_Q_over_H_qrubin;\n  int index_bg_phi_qrubin;\n  int index_bg_dphi_qrubin;")
idx4 = [i for i, l in enumerate(hd_bg) if "int index_bi_rho_fld;" in l][0]
hd_bg.insert(idx4 + 1, "  int index_bi_rho_cdm;\n  int index_bi_phi_qrubin;\n  int index_bi_dphi_qrubin;")

idx_endif = [i for i, l in enumerate(hd_bg) if "#endif" in l][-1]
act_def = """
static inline double qrubin_activation(double a, double a_t, double n) {
    if (n <= 0.0) return 0.0;
    if (a_t <= 0.0) return 1.0;
    return 1.0 / (1.0 + pow(a_t / a, n));
}
"""
hd_bg.insert(idx_endif, act_def)

# --- B. Input Parser ---
idx_def = [i for i, l in enumerate(inp) if "pba->Omega0_cdm = 0.1201075/pow(pba->h,2);" in l][0]
inp.insert(idx_def + 1, "  pba->M_Q = 0.0;\n  pba->a_t = 0.0;\n  pba->n_qrubin = 0.0;\n  pba->A0_qrubin = 0.0;\n  pba->B0_qrubin = 0.0;\n  pba->phi0_qrubin = 1.0;\n  pba->tau_Q = 1.0;\n  pba->Gamma0_qrubin = 0.0;\n  pba->S0_qrubin = 0.0;\n  pba->D0_qrubin = 0.0;\n  pba->has_qrubin = _FALSE_;")

parser_code = """  /* Q-Rubin V3.2 Parameter Parser */
  class_call(parser_read_double(pfc, "M_Q", &param1, &flag1, errmsg), errmsg, errmsg);
  if (flag1 == _TRUE_) { pba->M_Q = param1; }
  class_call(parser_read_double(pfc, "a_t", &param1, &flag1, errmsg), errmsg, errmsg);
  if (flag1 == _TRUE_) { pba->a_t = param1; }
  class_call(parser_read_double(pfc, "n_qrubin", &param1, &flag1, errmsg), errmsg, errmsg);
  if (flag1 == _TRUE_) { pba->n_qrubin = param1; }
  class_call(parser_read_double(pfc, "A0_qrubin", &param1, &flag1, errmsg), errmsg, errmsg);
  if (flag1 == _TRUE_) { pba->A0_qrubin = param1; }
  class_call(parser_read_double(pfc, "B0_qrubin", &param1, &flag1, errmsg), errmsg, errmsg);
  if (flag1 == _TRUE_) { pba->B0_qrubin = param1; }
  class_call(parser_read_double(pfc, "phi0_qrubin", &param1, &flag1, errmsg), errmsg, errmsg);
  if (flag1 == _TRUE_) { pba->phi0_qrubin = param1; }
  class_call(parser_read_double(pfc, "tau_Q", &param1, &flag1, errmsg), errmsg, errmsg);
  if (flag1 == _TRUE_) { pba->tau_Q = param1; }
  class_call(parser_read_double(pfc, "Gamma0_qrubin", &param1, &flag1, errmsg), errmsg, errmsg);
  if (flag1 == _TRUE_) { pba->Gamma0_qrubin = param1; }
  class_call(parser_read_double(pfc, "S0_qrubin", &param1, &flag1, errmsg), errmsg, errmsg);
  if (flag1 == _TRUE_) { pba->S0_qrubin = param1; }
  class_call(parser_read_double(pfc, "D0_qrubin", &param1, &flag1, errmsg), errmsg, errmsg);
  if (flag1 == _TRUE_) { pba->D0_qrubin = param1; }
  if (pba->M_Q != 0.0 && (pba->A0_qrubin != 0.0 || pba->B0_qrubin != 0.0 || pba->S0_qrubin != 0.0 || pba->Gamma0_qrubin != 0.0)) {
    pba->has_qrubin = _TRUE_;
  } else {
    pba->has_qrubin = _FALSE_;
  }"""
idx_parse = [i for i, l in enumerate(inp) if 'class_test(pba->Omega0_cdm<0,errmsg, "You cannot set the cold dark matter density to negative values.");' in l][0]
inp.insert(idx_parse + 1, parser_code)

# --- C. Background Engine ---
idx_bool = [i for i, l in enumerate(bg) if "pba->has_dcdm = _FALSE_;" in l][0]
bg.insert(idx_bool + 1, "  pba->has_qrubin = _FALSE_;\n  if (pba->M_Q != 0. && (pba->S0_qrubin != 0. || pba->B0_qrubin != 0. || pba->A0_qrubin != 0. || pba->Gamma0_qrubin != 0.)) pba->has_qrubin = _TRUE_;")
idx_bg_alloc = [i for i, l in enumerate(bg) if "class_define_index(pba->index_bg_rho_cdm,pba->has_cdm,index_bg,1);" in l][0]
bg.insert(idx_bg_alloc + 1, "  class_define_index(pba->index_bg_W_qrubin,pba->has_qrubin,index_bg,1);\n  class_define_index(pba->index_bg_Q_over_H_qrubin,pba->has_qrubin,index_bg,1);\n  class_define_index(pba->index_bg_phi_qrubin,pba->has_qrubin,index_bg,1);\n  class_define_index(pba->index_bg_dphi_qrubin,pba->has_qrubin,index_bg,1);")
idx_bi_alloc = [i for i, l in enumerate(bg) if "class_define_index(pba->index_bi_rho_fld,pba->has_fld,index_bi,1);" in l][0]
bg.insert(idx_bi_alloc + 1, "  class_define_index(pba->index_bi_rho_cdm,pba->has_cdm && pba->has_qrubin,index_bi,1);\n  class_define_index(pba->index_bi_phi_qrubin,pba->has_qrubin,index_bi,1);\n  class_define_index(pba->index_bi_dphi_qrubin,pba->has_qrubin,index_bi,1);")

ic_code = """  if (pba->has_qrubin == _TRUE_) {
    if (pba->has_cdm == _TRUE_) pvecback_integration[pba->index_bi_rho_cdm] = pba->Omega0_cdm*pow(pba->H0,2);
    pvecback_integration[pba->index_bi_phi_qrubin] = pba->phi0_qrubin;
    pvecback_integration[pba->index_bi_dphi_qrubin] = 0.0;
  }"""
idx_ic = [i for i, l in enumerate(bg) if "/* Set initial values of {B} variables: */" in l][0]
bg.insert(idx_ic + 1, ic_code)

map_code = """  if (pvecback_B != NULL && pba->has_qrubin == _TRUE_) {
    if (pba->has_cdm == _TRUE_) pvecback[pba->index_bg_rho_cdm] = pvecback_B[pba->index_bi_rho_cdm] / pow(a, 3.0);
    pvecback[pba->index_bg_phi_qrubin] = pvecback_B[pba->index_bi_phi_qrubin];
    pvecback[pba->index_bg_dphi_qrubin] = pvecback_B[pba->index_bi_dphi_qrubin];
  }"""
idx_map = [i for i, l in enumerate(bg) if "pvecback[pba->index_bg_rho_cdm] = pba->Omega0_cdm * pow(pba->H0,2) / pow(a,3);" in l][0]
bg.insert(idx_map + 1, map_code)

idx_weval = [i for i, l in enumerate(bg) if "pvecback[pba->index_bg_H] = sqrt(rho_tot-pba->K/a/a);" in l][0]
bg_eval_code = """  if (pba->has_qrubin == _TRUE_) {
    double phi_q = pvecback[pba->index_bg_phi_qrubin];
    double dphi_q = pvecback[pba->index_bg_dphi_qrubin];
    double W_c = qrubin_activation(a, pba->a_t, pba->n_qrubin);
    pvecback[pba->index_bg_W_qrubin] = W_c;
    double H_c = pvecback[pba->index_bg_H];
    double Q_bar_c = pow(pba->M_Q, 5.0) * (pba->B0_qrubin * W_c) * phi_q - pow(pba->M_Q, 4.0) * (pba->A0_qrubin * W_c) * H_c * dphi_q;
    pvecback[pba->index_bg_Q_over_H_qrubin] = (H_c > 0.0) ? (Q_bar_c / H_c) : 0.0;
  }"""
bg.insert(idx_weval + 1, bg_eval_code)

deriv_v32 = """  if (pba->has_qrubin == _TRUE_) {
    double phi_q = y[pba->index_bi_phi_qrubin];
    double dphi_q = y[pba->index_bi_dphi_qrubin];
    double W_c = qrubin_activation(a, pba->a_t, pba->n_qrubin);
    double Q_bar = pow(pba->M_Q, 5.0) * (pba->B0_qrubin * W_c) * phi_q - pow(pba->M_Q, 4.0) * (pba->A0_qrubin * W_c) * H * dphi_q;
    pvecback[pba->index_bg_Q_over_H_qrubin] = Q_bar / H;
    dy[pba->index_bi_phi_qrubin] = dphi_q;
    double dlnH_dlna = -1.5 * (1.0 + pvecback[pba->index_bg_p_tot] / pvecback[pba->index_bg_rho_tot]);
    dy[pba->index_bi_dphi_qrubin] = - (1.0 / (pba->tau_Q * H) + dlnH_dlna) * dphi_q - ((pba->Gamma0_qrubin * W_c) / (pba->tau_Q * H * H)) * phi_q + ((pba->S0_qrubin * W_c) / (pba->tau_Q * H * H));
    if (pba->has_cdm == _TRUE_) dy[pba->index_bi_rho_cdm] = pow(a, 3.0) * (Q_bar / H);
  }"""
idx_deriv = [i for i, l in enumerate(bg) if "H = pvecback[pba->index_bg_H];" in l][0]
bg.insert(idx_deriv + 1, deriv_v32)

idx_title = [i for i, l in enumerate(bg) if 'class_store_columntitle(titles,"(.)rho_cdm",pba->has_cdm);' in l][0]
bg.insert(idx_title + 1, '  class_store_columntitle(titles,"W_qrubin",pba->has_qrubin);\n  class_store_columntitle(titles,"Q_over_H_qrubin",pba->has_qrubin);\n  class_store_columntitle(titles,"phi_qrubin",pba->has_qrubin);\n  class_store_columntitle(titles,"dphi_qrubin",pba->has_qrubin);')
idx_data = [i for i, l in enumerate(bg) if "class_store_double(dataptr,pvecback[pba->index_bg_rho_cdm],pba->has_cdm,storeidx);" in l][0]
bg.insert(idx_data + 1, '    class_store_double(dataptr,pvecback[pba->index_bg_W_qrubin],pba->has_qrubin,storeidx);\n    class_store_double(dataptr,pvecback[pba->index_bg_Q_over_H_qrubin],pba->has_qrubin,storeidx);\n    class_store_double(dataptr,pvecback[pba->index_bg_phi_qrubin],pba->has_qrubin,storeidx);\n    class_store_double(dataptr,pvecback[pba->index_bg_dphi_qrubin],pba->has_qrubin,storeidx);')

# --- D. Perturbation Engine ---
idx_pt_hd = [i for i, l in enumerate(hd_pt) if "int index_pt_delta_cdm;" in l][0]
hd_pt.insert(idx_pt_hd + 1, "  int index_pt_delta_phi_qrubin;\n  int index_pt_dphi_qrubin;")

idx_index_start = [i for i, l in enumerate(pt) if "index_pt = 0;" in l][0]
pt.insert(idx_index_start, "  ppv->index_pt_delta_phi_qrubin = -1;\n  ppv->index_pt_dphi_qrubin = -1;")
idx_pt_alloc = [i for i, l in enumerate(pt) if "class_define_index(ppv->index_pt_delta_cdm,pba->has_cdm,index_pt,1);" in l][0]
pt.insert(idx_pt_alloc + 1, "  class_define_index(ppv->index_pt_delta_phi_qrubin, pba->has_qrubin, index_pt, 1);\n  class_define_index(ppv->index_pt_dphi_qrubin, pba->has_qrubin, index_pt, 1);")

idx_pt_ic = [i for i, l in enumerate(pt) if "ppv->y[ppv->index_pt_delta_cdm] =" in l][0]
ic_pt = """          if (pba->has_qrubin == _TRUE_ && ppv->index_pt_delta_phi_qrubin >= 0) {
            if (pa_old == NULL || ppw->pv == NULL || ppw->pv->index_pt_delta_phi_qrubin < 0) {
              ppv->y[ppv->index_pt_delta_phi_qrubin] = 0.0;
              ppv->y[ppv->index_pt_dphi_qrubin] = 0.0;
            } else {
              ppv->y[ppv->index_pt_delta_phi_qrubin] = ppw->pv->y[ppw->pv->index_pt_delta_phi_qrubin];
              ppv->y[ppv->index_pt_dphi_qrubin] = ppw->pv->y[ppw->pv->index_pt_dphi_qrubin];
            }
          }"""
pt.insert(idx_pt_ic + 2, ic_pt)

idx_tot_ic = [i for i, l in enumerate(pt) if "ppw->pv->y[ppw->pv->index_pt_delta_cdm] = 3./4.*ppw->pv->y[ppw->pv->index_pt_delta_g];" in l][0]
tot_ic_code = "      if (pba->has_qrubin == _TRUE_ && ppw->pv->index_pt_delta_phi_qrubin >= 0) { ppw->pv->y[ppw->pv->index_pt_delta_phi_qrubin] = 0.0; ppw->pv->y[ppw->pv->index_pt_dphi_qrubin] = 0.0; }"
pt.insert(idx_tot_ic + 1, tot_ic_code)

idx_pt_deriv = [i for i, l in enumerate(pt) if "dy[pv->index_pt_theta_cdm] = - a_prime_over_a*y[pv->index_pt_theta_cdm] + metric_euler;" in l][0]

deriv_pt = """
        /* --- Q-Rubin V3.2 Perturbation Coupling (Phase 3 Audit Corrected) --- */
        if (pba->has_qrubin == _TRUE_ && pba->has_cdm == _TRUE_ && pv->index_pt_delta_phi_qrubin >= 0) {
          double delta_phi_q = y[pv->index_pt_delta_phi_qrubin];
          double ddelta_phi_q = y[pv->index_pt_dphi_qrubin];
          
          double W_c = qrubin_activation(a, pba->a_t, pba->n_qrubin);
          double A_c = pba->A0_qrubin * W_c;
          double B_c = pba->B0_qrubin * W_c;
          double Gamma_c = pba->Gamma0_qrubin * W_c;
          
          double rho_cdm = pvecback[pba->index_bg_rho_cdm];
          double Q_bar = pvecback[pba->index_bg_Q_over_H_qrubin] * (a_prime_over_a / a);
          double dphi_bg_dtau = pvecback[pba->index_bg_dphi_qrubin] * a_prime_over_a;
          
          double metric_psi = (k2 > 0.0) ? (metric_euler / k2) : 0.0;
          
          /* Phase 2: Equation-exact delta Q and scalar transfer potential f */
          double delta_Q = pow(pba->M_Q, 5.0) * B_c * delta_phi_q - (pow(pba->M_Q, 4.0) * A_c / a) * (ddelta_phi_q - metric_psi * dphi_bg_dtau);
          double f_transfer = (pow(pba->M_Q, 4.0) * A_c / a) * delta_phi_q;
          
          /* Phase 3: Scalar velocity divergence (theta_Q) with zero-division regulator */
          double theta_q = 0.0;
          if (fabs(dphi_bg_dtau) > 1e-16) {
              theta_q = k2 * delta_phi_q / dphi_bg_dtau;
          }
          
          if (rho_cdm > 0.0) {
            /* Eq. 30: Receiving Sector Continuity Perturbation */
            dy[pv->index_pt_delta_cdm] += (a / rho_cdm) * (delta_Q - Q_bar * y[pv->index_pt_delta_cdm] + Q_bar * metric_psi);
            /* Eq. 31: Receiving Sector Euler Perturbation (momentum conservation restored) */
            if (pv->index_pt_theta_cdm >= 0) {
              dy[pv->index_pt_theta_cdm] += (a / rho_cdm) * (Q_bar * (theta_q - y[pv->index_pt_theta_cdm]) - k2 * f_transfer);
            }
          }
          
          /* Eq. 32: Linearized Hyperbolic Relaxation-Diffusion Equation */
          dy[pv->index_pt_delta_phi_qrubin] = ddelta_phi_q;
          dy[pv->index_pt_dphi_qrubin] = - (2.0 * a_prime_over_a + a / pba->tau_Q) * ddelta_phi_q - ((a * a * Gamma_c + a * a * pba->D0_qrubin * k2) / pba->tau_Q) * delta_phi_q;
        }"""
pt.insert(idx_pt_deriv + 1, deriv_pt)

bg_file.write_text("\n".join(bg) + "\n")
hd_bg_file.write_text("\n".join(hd_bg) + "\n")
inp_file.write_text("\n".join(inp) + "\n")
hd_pt_file.write_text("\n".join(hd_pt) + "\n")
pt_file.write_text("\n".join(pt) + "\n")

print("\n[SUCCESS] Phase 2/3 Equation-Exact Q-Rubin V3.2 Engine Injected.")
