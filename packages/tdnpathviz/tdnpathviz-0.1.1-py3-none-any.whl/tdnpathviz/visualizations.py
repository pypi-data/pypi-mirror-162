import plotly.graph_objects as go
import random
import teradataml as tdml


def colors(n, alpha=0.8, random_seed=124):
    random.seed(random_seed)
    ret = []
    r = int(random.random() * 256)
    g = int(random.random() * 256)
    b = int(random.random() * 256)
    step = 256 / n
    for i in range(n):
        r += step
        g += step
        b += step
        r = int(r) % 256
        g = int(g) % 256
        b = int(b) % 256
        ret.append("rgba(" + str(r) + "," + str(g) + "," + str(b) + "," + str(alpha) + ")")
    return ret


def plot_first_main_paths(myPathAnalysis, path_column='mypath', id_column='travelid', nb_paths=15):
    df_agg = myPathAnalysis.result.select([id_column, path_column]).groupby(path_column).count()

    df_agg.shape[0]

    query = f"""SEL 
        row_number() OVER (PARTITION BY 1 ORDER BY count_{id_column} DESC) as id
    ,	REGEXP_REPLACE(lower(A.{path_column}),'\[|\]', '') as str
    ,	count_{id_column} as weight
    FROM {df_agg._table_name} A
    QUALIFY id < {nb_paths}+1"""

    df_selection = tdml.DataFrame.from_query(query)

    query2 = f"""
    sel
        CC.id
    ,	CC.node_source
    ,	CC.node_target
    ,	CC.beg
    ,	CC."end"
    ,	sum(CC.weight) as weight
    FROM 
    (
    sel
        B.*
    ,	LAG(id_end,1,0) OVER (PARTITION BY B."path" ORDER BY B."path",B."index") as id_beg
    ,	B."beg" || '_' || TRIM(CAST(id_beg AS VARCHAR(10))) as node_source
    ,	B."end" || '_' || TRIM(CAST(id_end AS VARCHAR(10))) as node_target
    FROM 
    (
        sel 
            A.*
        ,	row_number() OVER (PARTITION BY A."path" ORDER BY A."path",A."index") as id_end
        from (
        SELECT

            lag(AA.token,1) IGNORE NULLS OVER (PARTITION BY AA.outkey ORDER BY AA.tokennum) as "beg"
        ,	AA.token as "end"
        ,	AA.outkey as "path"
        ,	B.weight
        ,	AA.tokennum as "index"
        ,   B.id
        FROM (

        SELECT 
            d.*
        FROM TABLE (strtok_split_to_table({df_selection._table_name}.id, {df_selection._table_name}.str, ',')
        RETURNS (outkey integer, tokennum integer, token varchar(20)character set unicode) ) as d 

        ) AA
        ,{df_selection._table_name} B
        WHERE AA.outkey = B.id
        QUALIFY beg IS NOT NULL
    ) A
    ) B
    --ORDER BY "path","index"
    ) CC
    GROUP BY 1,2,3,4,5
    """

    df_ready = tdml.DataFrame.from_query(query2)

    df_ready_local = df_ready.to_pandas().sort_values(by='id')

    labs = dict()
    labels = list(set(df_ready_local.node_source.tolist() + df_ready_local.node_target.tolist()))

    for i, label in enumerate(labels):
        labs[label] = i

    labels = ['_'.join(x.split('_')[0:(len(x.split('_')) - 1)]) for x in labels]

    df_ready_local['color'] = df_ready_local.id.map(
        {id: col for id, col in zip(list(set(df_ready_local.id)), colors(len(set(df_ready_local.id)), random_seed=45))})

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels,
            color=colors(len(labels), random_seed=123)
        ),
        link=dict(
            source=df_ready_local.node_source.map(labs),  # indices correspond to labels, eg A1, A2, A2, B1, ...
            target=df_ready_local.node_target.map(labs),
            value=df_ready_local.weight,
            color=df_ready_local.color
        ))])

    fig.update_layout(font_size=10, width=1200,
                      height=800)
    fig.show()