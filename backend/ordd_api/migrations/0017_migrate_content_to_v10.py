# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-08-11 11:50
from __future__ import unicode_literals

from django.db import migrations
from django.core import serializers
from django.core.management import call_command

import csv
import json


def forwards_func(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    KeyDataset = apps.get_model("ordd_api", "KeyDataset")
    KeyCategory = apps.get_model("ordd_api", "KeyCategory")
    KeyDatasetName = apps.get_model("ordd_api", "KeyDatasetName")
    KeyTagGroup = apps.get_model("ordd_api", "KeyTagGroup")
    KeyTag = apps.get_model("ordd_api", "KeyTag")
    KeyLevel = apps.get_model("ordd_api", "KeyLevel")
    Dataset = apps.get_model("ordd_api", "Dataset")

    db_alias = schema_editor.connection.alias

    #  Rename entries
    #
    #    KeyCategory
    item = KeyCategory.objects.using(db_alias).get(name='Base Data')
    item.name = 'Base data'
    item.save()

    #    KeyTag
    item = KeyTag.objects.using(db_alias).get(name='Road infrastructure')
    item.name = 'Roads'
    item.save()

    item = KeyTag.objects.using(db_alias).get(name='Harbours')
    item.name = 'Harbors'
    item.save()

    #    KeyDatasetName
    item = KeyDatasetName.objects.using(db_alias).get(name='Hazard Scenarios')
    item.name = 'Historical records of hazard events'
    item.save()

    #    KeyDatasetName simple capitalization
    items = KeyDatasetName.objects.using(db_alias).all()
    for item in items:
        item.name = item.name.capitalize()
        item.save()

    return

    kd = []
    kd_code = []
    kt = []

    with open('contents/key_datasets/resilience-index-'
              'datasets-list-v10 - Datasets.csv', 'r') as kdfile,\
        open('contents/key_datasets/resilience-index-'
             'datasets-list-v10 - Tags.csv', 'r') as ktfile:
        kdcsv = csv.reader(kdfile, delimiter=',')
        ktcsv = csv.reader(ktfile, delimiter=',')

        for row in kdcsv:
            if len(row) == 0:
                continue
            kd.append(row)
            kd_code.append(row[0])
        kd = kd[1:]
        kd_code = kd_code[1:]

        for row in ktcsv:
            if len(row) == 0:
                continue
            kt.append(row)
        kt = kt[1:]

        # keydataset

        print("\n\n")
        print("keydatasets")

        national_level = KeyLevel.objects.using(db_alias).get(name='National')

        print("\nKEYDATASETS: check keydataset not yet inserted")
        objs = KeyDataset.objects.using(db_alias).all()
        for keydataset in kd:
            for obj in objs:
                kd_cur = obj.code
                if kd_cur == keydataset[0]:
                    dsname = KeyDatasetName.objects.using(db_alias).get(
                        name=keydataset[2])
                    category = KeyCategory.objects.using(db_alias).get(
                        name=keydataset[1])
                    if obj.level_id != 2:
                        print("  WRONG LEVEL_ID: code: [%s]  level: %d"
                              % (kd_cur, obj.level_id))
                    obj.level = national_level
                    obj.description = keydataset[4]
                    obj.dataset = dsname
                    obj.category = category
                    obj.save()
                    break
            else:
                print('  Keydataset "%s" not already present in dataset.'
                      % keydataset[0])
        print("  Done")
        raise ValueError("just to avoid commit of transaction")
        # Tags

        print("\nTAGS: check tags not yet inserted")
        objs = KeyTag.objects.using(db_alias).all()
        for tag in kt:
            for obj in objs:
                tag_cur = [obj.group.name, obj.name]
                if tag_cur[0] == tag[0] and tag_cur[1] == tag[1]:
                    break
            else:
                print('  Tag "%s, %s" not already present in dataset.' % (
                    tag[0], tag[1]))
        print("  Done")

        print("\nTAGS: intersection with current dataset (old keydataset"
              " tags referenced by current dataset with new tags)")
        obj = KeyTag.objects.using(db_alias).filter(
            dataset__in=Dataset.objects.using(db_alias).filter(
                keydataset__in=kd_code)).distinct().order_by('group', 'name')
        tags_cur = [[o.group.name, o.name] for o in obj]

        for tag_cur in tags_cur:
            for tag in kt:
                if tag_cur[0] == tag[0] and tag_cur[1] == tag[1]:
                    break
            else:
                raise ValueError('Tag "%s, %s" not found in the new list.'
                                 % (tag_cur[0], tag_cur[1]))
        print("  Done")

        print("\nTAGS: check relations of tags to be removed")
        objs = KeyTag.objects.using(db_alias).all()
        for obj in objs:
            tag_cur = [obj.group.name, obj.name]
            found = False
            for tag in kt:
                if tag_cur[0] == tag[0] and tag_cur[1] == tag[1]:
                    found = True
                    break
            else:
                if (len(obj.keydataset_set.all()) != 0 or
                        len(obj.dataset_set.all()) != 0):
                    raise ValueError(
                        "Tag [%s - %s] referenced by keydataset or dataset"
                        % (tag_cur[0], tag_cur[1]))

            if found is False:
                print("  Tag [%s - %s] could be removed safety"
                      % (tag_cur[0], tag_cur[1]))







def forwards_func_old(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    KeyDataset = apps.get_model("ordd_api", "KeyDataset")
    KeyCategory = apps.get_model("ordd_api", "KeyCategory")
    KeyDatasetName = apps.get_model("ordd_api", "KeyDatasetName")
    KeyTagGroup = apps.get_model("ordd_api", "KeyTagGroup")
    KeyTag = apps.get_model("ordd_api", "KeyTag")
    KeyLevel = apps.get_model("ordd_api", "KeyLevel")
    Dataset = apps.get_model("ordd_api", "Dataset")

    db_alias = schema_editor.connection.alias

    # check for contentless database
    kd_check = KeyDataset.objects.using(db_alias).all()
    if kd_check.count() == 0:
        return
    
    klevel_loc = KeyLevel.objects.using(db_alias).get(name='Local')
    klevel_nat = KeyLevel.objects.using(db_alias).get(name='National')
    klevel_int = KeyLevel.objects.using(db_alias).get(name='International')

    ktaggrp_ha = KeyTagGroup.objects.using(db_alias).get(name='hazard')

    kcat_ba = KeyCategory.objects.using(db_alias).get(code='BA')
    kcat_ha = KeyCategory.objects.using(db_alias).get(code='HA')
    kcat_ri = KeyCategory.objects.using(db_alias).get(code='RI')
    kcat_ex = KeyCategory.objects.using(db_alias).get(code='EX')

    # NEW TIME REFERENCE TAG GROUP
    ktaggrp_timeref = KeyTagGroup.objects.using(db_alias).create(
        name='time reference')

    KeyTag.objects.using(db_alias).create(
        name='Present', group=ktaggrp_timeref, is_peril=False)

    KeyTag.objects.using(db_alias).create(
        name='Future projection', group=ktaggrp_timeref,
        is_peril=False)

    # NEW BA_5
    kdname = KeyDatasetName.objects.using(db_alias).get(name='Bathymetry')
    kd = KeyDataset.objects.using(db_alias).create(
        code='BA_5', category=kcat_ba, dataset=kdname,
        tag_available=ktaggrp_ha,
        description="Bathymetry map describing the terrain that lies"
        " underwater, or the depth of water relative to sea level, with"
        " a resolution of at least 10 meters.",
        level=klevel_nat, format="raster (.tif)", comment="", weight=10)

    kd.applicability.add(KeyTag.objects.using(db_alias).get(name='Coastal '
                                                            'flooding'),
                         KeyTag.objects.using(db_alias).get(name='Tsunami'))

    # NEW BA_6
    kd = KeyDataset.objects.using(db_alias).create(
        code='BA_6', category=kcat_ba, dataset=kdname,
        tag_available=ktaggrp_ha,
        description="Bathymetry map describing the terrain that lies"
        " underwater, or the depth of water relative to sea level, with"
        " a resolution of 100 meters or higher.",
        level=klevel_nat, format="raster (.tif)", comment="", weight=10)

    kd.applicability.add(KeyTag.objects.using(db_alias).get(name='Coastal '
                                                            'flooding'),
                         KeyTag.objects.using(db_alias).get(name='Tsunami'))

    # NEW HA_23A
    kdname_scen = KeyDatasetName.objects.using(db_alias).create(
        name="Hazard scenarios")

    kd = KeyDataset.objects.using(db_alias).create(
        code='HA_23A', category=kcat_ha, dataset=kdname_scen,
        tag_available=ktaggrp_ha,
        description="Historical records of significant natural hazard"
        " events in the country including the type, intensity, footprint,"
        " description and date of the hazard events. Historical records"
        " may refer to only one or more hazard types. Data may also contain"
        " non observed but plausible scenarios of hazard events.",
        level=klevel_nat, comment="", weight=10)

    # NEW HA_23B
    kdname_rec = KeyDatasetName.objects.using(db_alias).get(
        name="Historical records")

    kd = KeyDataset.objects.using(db_alias).create(
        code='HA_23B', category=kcat_ha, dataset=kdname_rec,
        tag_available=ktaggrp_ha,
        description="Historical records of all natural hazard events in the"
        " country including at least the type, intensity, description, date"
        " and location of the hazard events. Historical records may refer"
        " to only one or more hazard types.",
        level=klevel_loc, comment="", weight=10)

    # NEW RI_2
    kdname = KeyDatasetName.objects.using(db_alias).get(
        name="records of previous natural disasters")

    kd = KeyDataset.objects.using(db_alias).create(
        code='RI_2', category=kcat_ri, dataset=kdname,
        tag_available=ktaggrp_ha,
        description="Information about affected exposure during"
        " previous hazard.",
        level=klevel_nat, comment="", weight=10)

    # NEW EX_3D
    kdname = KeyDatasetName.objects.using(db_alias).create(
        name='Company register')

    kd = KeyDataset.objects.using(db_alias).create(
        code='EX_3D', category=kcat_ex, dataset=kdname,
        tag_available=ktaggrp_timeref,
        description="List of registered companies for the country"
        " including their addresses and economic sector.",
        level=klevel_nat, comment="", weight=10)

    kd.applicability.add(*list(KeyTag.objects.using(
        db_alias).filter(is_peril=True)))

    # MOVE DATASETS BETWEEN KEYDATASETS
    for kd_code, kd_code_new in mv_keydatasets.items():
        print(kd_code)
        kd = KeyDataset.objects.using(db_alias).get(code=kd_code)
        kd_new = KeyDataset.objects.using(db_alias).get(
            code=kd_code_new)

        datasets = Dataset.objects.using(db_alias).filter(
            keydataset=kd)
        for ds in datasets:
            print(ds)
            ds.keydataset = kd_new
            ds.save()

    # REMOVE OBSOLETE KEYDATASETS
    kds = KeyDataset.objects.using(db_alias).filter(code__in=rm_keydatasets)

    print("RM COUNT: %d" % kds.count())
    data = serializers.serialize("json", kds, indent=4)
    out = open("v9_keydatasets_deleted.json", "w")
    out.write(data)
    out.close()

    kds.delete()

    # NEW DATASETNAMES
    # save previous KeyDatasetName and keydataset
    kds = KeyDataset.objects.using(db_alias).all()

    data = serializers.serialize("json", kds, indent=4)
    out = open("v9_keydatasets_pre_kdname-change.json", "w")
    out.write(data)
    out.close()

    kdsname = KeyDatasetName.objects.using(db_alias).all()
    data = serializers.serialize("json", kdsname, indent=4)
    out = open("v9_keydatasetnames_pre_kdname-change.json", "w")
    out.write(data)
    out.close()

    # CHANGE DATASETNAMES IN KEYDATASETS
    new_names = []
    # update keydataset with new keydatasetnames and create them if needed
    for code, name in new_keydatasetnames.items():
        kd = KeyDataset.objects.using(db_alias).get(code=code)
        try:
            kdname = KeyDatasetName.objects.using(db_alias).get(
                name__iexact=name)
            kdname.name = name
            kdname.category = None
            kdname.save()
            print("[%s:%s] already found" % (kdname.name, kdname.category))
        except:
            kdname = KeyDatasetName.objects.using(db_alias).create(
                name=name, category=None)
            kdname.save()
            print("[%s:%s] not found, create" % (kdname.name, kdname.category))
            new_names.append([kdname.name, kdname.category])

        kd.dataset = kdname
        kd.save()

    with open("new_keydatasetnames.json", "w") as f:
        json.dump(new_names, f)

    # delete keydatasetname without any keydataset reference
    kdnames = KeyDatasetName.objects.using(db_alias).filter(keydatasets=None)
    kdnames.delete()

    kdnames = KeyDatasetName.objects.using(db_alias).exclude(category=None)
    for kdname in kdnames:
        kdname.category = None
        kdname.save()

    for code, desc in new_keydataset_descr.items():
        kd = KeyDataset.objects.using(db_alias).get(code=code)
        kd.description = desc.strip()
        kd.save()


def backwards_func(apps, schema_editor):
    KeyDataset = apps.get_model("ordd_api", "KeyDataset")
    KeyCategory = apps.get_model("ordd_api", "KeyCategory")
    KeyDatasetName = apps.get_model("ordd_api", "KeyDatasetName")
    KeyTagGroup = apps.get_model("ordd_api", "KeyTagGroup")
    KeyTag = apps.get_model("ordd_api", "KeyTag")
    KeyLevel = apps.get_model("ordd_api", "KeyLevel")
    Dataset = apps.get_model("ordd_api", "Dataset")

    db_alias = schema_editor.connection.alias

    #    KeyDatasetName
    item = KeyDatasetName.objects.using(db_alias).get(
        name='Historical records of hazard events')
    item.name = 'Hazard Scenarios'
    item.save()

    #    KeyTag
    item = KeyTag.objects.using(db_alias).get(name='Harbors')
    item.name = 'Harbours'
    item.save()

    item = KeyTag.objects.using(db_alias).get(name='Roads')
    item.name = 'Road infrastructure'
    item.save()

    #    KeyCategory
    item = KeyCategory.objects.using(db_alias).get(name='Base data')
    item.name = 'Base Data'
    item.save()


class Migration(migrations.Migration):

    dependencies = [
        ('ordd_api', '0016_rename_dataset_fields'),
    ]

    operations = [
        migrations.RunPython(forwards_func, backwards_func),
    ]
