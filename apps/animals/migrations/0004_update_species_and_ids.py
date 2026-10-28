"""
Data migration: update 8 animals to Cow / Buffalo species.

Safe to run on:
  - An existing database (where 0003 has already seeded all 12 animals as Yak).
  - A fresh database (where 0003 runs first, seeding all 12 as Yak, then this
    migration immediately renames them).

No duplicate animal_id can arise because we process animals in the correct
order (rename source away before a destination could clash) and the 8 new IDs
("Cow NNN", "Buf NNN") are guaranteed not to exist after 0003.
"""

from django.db import migrations


# Animals that stay Yak: Yak 527, Yak 697, Yak 729, Yak 834
UPDATES = [
    # (old_animal_id,  new_animal_id,  new_species,  new_breed)
    ('Yak 751',  'Cow 751',  'Cow',     'Cow'),
    ('Yak 796',  'Cow 796',  'Cow',     'Cow'),
    ('Yak 806',  'Cow 806',  'Cow',     'Cow'),
    ('Yak 842',  'Cow 842',  'Cow',     'Cow'),
    ('Yak 862',  'Buf 862',  'Buffalo', 'Buffalo'),
    ('Yak 870',  'Buf 870',  'Buffalo', 'Buffalo'),
    ('Yak 875',  'Buf 875',  'Buffalo', 'Buffalo'),
    ('Yak 887',  'Buf 887',  'Buffalo', 'Buffalo'),
]


def update_species_and_ids(apps, schema_editor):
    Animal = apps.get_model('animals', 'Animal')
    for old_id, new_id, new_species, new_breed in UPDATES:
        updated = Animal.objects.filter(animal_id=old_id).update(
            animal_id=new_id,
            species=new_species,
            breed=new_breed,
        )
        # If the animal doesn't exist (e.g. manually deleted), skip silently.
        # If the target ID already exists (re-run scenario), also skip.


def reverse_update(apps, schema_editor):
    """Reverse: rename Cow/Buf back to Yak."""
    Animal = apps.get_model('animals', 'Animal')
    for old_id, new_id, new_species, new_breed in reversed(UPDATES):
        Animal.objects.filter(animal_id=new_id).update(
            animal_id=old_id,
            species='Yak',
            breed='Yak',
        )


class Migration(migrations.Migration):

    dependencies = [
        ('animals', '0003_import_yak_data'),
    ]

    operations = [
        migrations.RunPython(update_species_and_ids, reverse_code=reverse_update),
    ]

