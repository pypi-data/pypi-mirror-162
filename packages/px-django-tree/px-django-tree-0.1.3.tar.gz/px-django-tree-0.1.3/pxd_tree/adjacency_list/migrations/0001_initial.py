from django.db import migrations


# TODO: Analyze function performance and improve it.
CREATE_AL_TRACE_FUNCTION_SQL = [
    """--sql
    -- Trace all tree members in direction of `from_id -> to_id`.
    CREATE OR REPLACE FUNCTION pxd_al_trace(
        use_parent int,
        table_name text,
        from_id text default 'parent_id',
        to_id text default 'id',
        schema_name text default 'public'
    ) RETURNS int[] as $BODY$
    DECLARE
        process_parents int[] := ARRAY[ use_parent ];
        children int[] := '{}';
        new_children int[];
    BEGIN
        WHILE ( array_upper( process_parents, 1 ) IS NOT NULL ) loop
            execute format(
                'SELECT array_agg(%I) FROM %I.%I WHERE %I = ANY( $1 ) AND %I <> ALL( $2 )',
                to_id, schema_name, table_name, from_id, to_id
            ) using process_parents, children into new_children;
            children := children || new_children;
            process_parents := new_children;
        END LOOP;
        RETURN children;
    END;
    $BODY$ LANGUAGE plpgsql;
    """,
]
DROP_AL_TRACE_FUNCTION_SQL = 'DROP FUNCTION IF EXISTS pxd_al_trace;'

CREATE_AL_DESCENDANTS_FUNCTION_SQL = [
    """--sql
    -- Getting all adjacent list descendants
    CREATE OR REPLACE FUNCTION pxd_al_descendants(
        use_parent int,
        table_name text,
        from_id text default 'parent_id',
        to_id text default 'id',
        schema_name text default 'public'
    ) RETURNS int[] as $BODY$
        select pxd_al_trace(use_parent, table_name, from_id, to_id, schema_name);
    $BODY$ LANGUAGE sql;
    """,
]
DROP_AL_DESCENDANTS_FUNCTION_SQL = 'DROP FUNCTION IF EXISTS pxd_al_descendants;'

CREATE_AL_ANCESTORS_FUNCTION_SQL = [
    """--sql
    -- Getting all adjacent list parents
    CREATE OR REPLACE FUNCTION pxd_al_ancestors(
        use_parent int,
        table_name text,
        from_id text default 'parent_id',
        to_id text default 'id',
        schema_name text default 'public'
    ) RETURNS int[] as $BODY$
        select pxd_al_trace(use_parent, table_name, to_id, from_id, schema_name);
    $BODY$ LANGUAGE sql;
    """,
]
DROP_AL_ANCESTORS_FUNCTION_SQL = 'DROP FUNCTION IF EXISTS pxd_al_ancestors;'


class Migration(migrations.Migration):
    dependencies = []
    operations = [
        migrations.RunSQL(
            CREATE_AL_TRACE_FUNCTION_SQL,
            DROP_AL_TRACE_FUNCTION_SQL,
        ),
        migrations.RunSQL(
            CREATE_AL_ANCESTORS_FUNCTION_SQL,
            DROP_AL_ANCESTORS_FUNCTION_SQL,
        ),
        migrations.RunSQL(
            CREATE_AL_DESCENDANTS_FUNCTION_SQL,
            DROP_AL_DESCENDANTS_FUNCTION_SQL,
        ),
    ]
