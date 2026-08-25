FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    KENKOMIRAI_MOBILITY_CSV=/workspace/data/la_mobilityreports.csv \
    KENKOMIRAI_POPULATION_SHAPEFILE=/workspace/data/population/2020_Population_and_Poverty_at_Split_Tract.shp
RUN groupadd --system --gid 10001 kenko \
    && useradd --system --uid 10001 --gid kenko --home-dir /workspace kenko \
    && mkdir -p /workspace/ml/models \
    && chown -R kenko:kenko /workspace
WORKDIR /workspace
COPY ml/requirements.txt ./ml/requirements.txt
RUN python -m pip install --no-cache-dir -r ml/requirements.txt
COPY --chown=kenko:kenko backend ./backend
COPY --chown=kenko:kenko ml ./ml
COPY --chown=kenko:kenko "initial datasets/la_mobilityreports.csv" ./data/la_mobilityreports.csv
COPY --chown=kenko:kenko "initial datasets/2020_Population/2020_Population_and_Poverty_at_Split_Tract.shp" ./data/population/2020_Population_and_Poverty_at_Split_Tract.shp
COPY --chown=kenko:kenko "initial datasets/2020_Population/2020_Population_and_Poverty_at_Split_Tract.shx" ./data/population/2020_Population_and_Poverty_at_Split_Tract.shx
COPY --chown=kenko:kenko "initial datasets/2020_Population/2020_Population_and_Poverty_at_Split_Tract.dbf" ./data/population/2020_Population_and_Poverty_at_Split_Tract.dbf
COPY --chown=kenko:kenko "initial datasets/2020_Population/2020_Population_and_Poverty_at_Split_Tract.prj" ./data/population/2020_Population_and_Poverty_at_Split_Tract.prj
USER kenko

ENTRYPOINT ["python", "ml/training/train_rl_agent.py"]
CMD ["--timesteps", "50000", "--output", "/workspace/ml/models/ppo_seird"]
