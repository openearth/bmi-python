FROM deltares/delft3dfm:latest
FROM continuumio/miniconda3:latest
RUN conda install numpy jupyter notebook ipython
RUN pip install bmi-python
COPY --from=0 /opt/delft3dfm_latest /opt/delft3dfm_latest
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/opt/delft3dfm_latest/lnx64/lib
ENV PATH=$PATH:/opt/delft3dfm_latest/lnx64/bin
WORKDIR /root/
EXPOSE 9999
CMD bmi-runner dflowfm
