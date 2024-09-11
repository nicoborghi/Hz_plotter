# %%
import cosmo
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import base64
from io import StringIO
from astropy.table import Table
import mpl_fontkit as fk

fk.install("Lato")

lambda_cosmo = {"H0": 67.27, "Om0": 0.3}

all_probes =  ["SNIa", "CMB", "SBF", "GW", "BAO", "CC"]
all_colors =  ['#4477AA', '#EE6677', '#228833', '#CCBB44', '#66CCEE', '#000000']
all_markers = ["^", ".", "D", "X", "p", "v"]

def_size = 4
def_size_lowz = .5

plot_z = []
plot_Hz = []
plot_err = []
plot_label = []
plot_color = []
plot_marker = []
plot_sizes = []

st.set_page_config(page_title="H(z) Plotter", page_icon=":dizzy:", layout="wide")
st.title("*H(z)* Plotter")
st.sidebar.header("🪄 Settings")


st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {
            width: 550px !important; # Set the width to your desired value
        }
    </style>
    """,
    unsafe_allow_html=True,
)

def svg_write(fig, center=True):
    """
    Renders a matplotlib figure object to SVG.
    Disable center to left-margin align like other objects.
    """
    imgdata = StringIO()
    fig.savefig(imgdata, format="svg")

    imgdata.seek(0)
    svg_string = imgdata.getvalue()
    b64 = base64.b64encode(svg_string.encode("utf-8")).decode("utf-8")

    css_justify = "center" if center else "left"
    css = '<p style="text-align:center; display: flex; justify-content: {};">'.format(css_justify)
    html = r'{}<img src="data:image/svg+xml;base64,{}" style="border: 0.5px dashed grey;" width=1280/>'.format(css, b64)

    st.write(html, unsafe_allow_html=True)


def get_data(t):

    name_short = t.meta["name_short"]

    if name_short != "BAO":
        z = t["z"]
        Hz = t["Hz"]

        if 'errHz' in t.dtype.names:
            errHz = np.atleast_2d([t["errHz"], t["errHz"]])
        elif 'errHz_down' in t.dtype.names:
            errHz = np.atleast_2d([t["errHz_down"], t["errHz_up"]])
        else:
            raise ValueError("No error column found")

    else:
        z = t["z"]
        dHrD = t["dHrD"]
        errdHrD = t["errdHrD"]
        errdHrD_p = errdHrD / dHrD

        Hz = 299792.458  / (dHrD * 147)   # - 5  # fixthis
        errHz = errdHrD_p * Hz     # * 2  # fixthis

    
    if "label" in t.meta:
        label = t.meta["label"]
    else:
        label = f"{name_short} - {t[0]['reference']}"

    return z, Hz, errHz, label



st.sidebar.markdown(f"#### Load data")
probes = st.sidebar.multiselect("Probes", all_probes, default=all_probes)#, label_visibility="hidden")
with st.sidebar.container(height=350):
    for i in range(len(probes)):

        t = Table.read(f"data/{probes[i]}.ecsv")
        
        z, Hz, err, label = get_data(t)

        # color piker with default color

        c0,c1,c2,c3,c4 = st.columns([0.8,2,1,1,1])
        with c0:
            st.write(f"**{probes[i]}:**")
        with c1:
            label = st.text_input("Label", label, key=f"label_{i}")
            # sizes = st.slider("Size", 1, 10, def_size)
        with c2:
            marker = st.selectbox("Marker", all_markers, index=i, key=f"marker_{i}", help="Any matplotlib marker is ok")
        with c3:
            size = st.text_input("Size", def_size, key=f"size_{i}")
        with c4:
            color = st.color_picker("Color", all_colors[i], key=f"color_{i}")

        if label == "":
            label = None
        
        plot_z.append(z)
        plot_Hz.append(Hz)
        plot_err.append(err)
        plot_label.append(label)
        plot_color.append(color)
        plot_marker.append(marker)
        plot_sizes.append(size)


# st.sidebar.markdown(f"#### Plot model")
# with st.sidebar.container(height=120):
#     cm1, cm2, cm3, cm4 = st.columns([1,1,1,1])

#     with cm1:
#         H0 = st.number_input("H0", value=67.27)
#     with cm2:
#         Om0 = st.number_input("Om0", value=0.3)


st.sidebar.markdown(f"#### Plot settings")
with st.sidebar.container(height=320):
# 
# 
    cc4_1, cc_4_2, cc_4_3, cc_4_4 = st.columns([1,1,1.3,0.7])
    with cc4_1:
        width = st.number_input("Width", value=10)
    with cc_4_2:
        height = st.number_input("Height", value=5)
    with cc_4_3:
        font = st.selectbox("Font", fk.list_fonts())
    with cc_4_4:
        latex = bool(st.selectbox("Latex", [0, 1], index=0))

    cc4_1, cc_4_2, cc_4_3, cc_4_4 = st.columns([1,1,1,1])
    with cc4_1:
        xlim_min = st.number_input("min(x)", value=-0.1)
        xxlim_min = st.number_input("axins min(x)", value=-0.02)
        ixlim_min = st.number_input("axins %min(x)", value=0.08)
    with cc_4_2:
        xlim_max = st.number_input("max(x)", value=2.6)
        xxlim_max = st.number_input("axins max(x)", value=0.04)
        ixlim_max = st.number_input("axins %width(x)", value=0.5)
    with cc_4_3:
        ylim_min = st.number_input("min(y)", value=0)
        yylim_min = st.number_input("axins min(y)", value=57)
        iylim_min = st.number_input("axins %min(y)", value=0.15)

    with cc_4_4:
        ylim_max = st.number_input("max(y)", value=341)
        yylim_max = st.number_input("axins max(y)", value=83)
        iylim_max = st.number_input("axins %width(y)", value=0.45)


####################
#################### Figure
####################

plt.rc('text', usetex=latex)
plt.rc('font', family=font)

plt.rcParams["mathtext.fontset"] = "custom"
plt.rcParams["mathtext.rm"] = font
plt.rcParams["mathtext.it"] = font

fig, ax = plt.subplots(figsize=(width, height), dpi=300)
ax.set_xlim(xlim_min,xlim_max)
ax.set_ylim(ylim_min,ylim_max)
axins = ax.inset_axes([ixlim_min, ixlim_max, iylim_min, iylim_max])
axins.xaxis.set_visible(False)
axins.set_xlim(xxlim_min, xxlim_max)
axins.set_ylim(yylim_min, yylim_max)
ax.indicate_inset_zoom(axins, edgecolor="dimgrey")

zz = np.linspace(0, 2.5, 1000)
ax.plot(zz, cosmo.H(zz, lambda_cosmo), ls="--", color='silver', zorder=0)
zz_ins = np.linspace(0.0, 0.05, 100)
axins.plot(zz_ins, cosmo.H(zz_ins, lambda_cosmo), ls="--", color='silver', zorder=0)


h, l = [], []

for i in range(len(probes)):

    z  = plot_z[i]
    Hz = plot_Hz[i]
    err = plot_err[i]
    label = plot_label[i]
    color = plot_color[i]
    marker = plot_marker[i]
    size = plot_sizes[i]

    if z[0] < 0.01:
        
        if probes[i] == "SBF":
            z += 0.01
        elif probes[i] == "GW":
            z += 0.02

        axins.errorbar(z, Hz, yerr=err, marker=marker, markersize=size, capsize=2, ls='', lw=1, color=color, label=label)

        ax.errorbar(z, Hz, yerr=err, marker=marker, markersize=.5, capsize=2, ls='', color=color)

    else:
        ax.errorbar(z, Hz, yerr=err, marker=marker, markersize=size, capsize=2, ls='', lw=1, color=color, label=label)
        
        
h+=axins.get_legend_handles_labels()[0]
l+=axins.get_legend_handles_labels()[1] 
h+=ax.get_legend_handles_labels()[0]
l+=ax.get_legend_handles_labels()[1] 
ax.set_xlabel(r'$z$')
ax.set_ylabel(r'$H(z)$  [km s$^{-1}$ Mpc$^{-1}$]', fontsize=12)
ax.legend(h,l,loc='center left', bbox_to_anchor=(1, 0.5))


fig.tight_layout()
svg_write(fig, center = False)


### Download button
cD1, cD2 = st.columns([.2,1])

with cD1:
    fmt = st.selectbox("Select format", ["jpg", "png", "pdf", "svg", "eps"], index=0, label_visibility="hidden")
    fname = f"Hz_plotter.{fmt}"
    plt.savefig(fname, transparent=True)

with cD1:
    with open(fname, "rb") as img:
        btn = st.download_button( label="Download image", data=img, file_name=fname, mime=f"image/{fmt}", type="primary")
