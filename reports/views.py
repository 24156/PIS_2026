import io
import json
from datetime import datetime

from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from django.http import HttpResponse
from django.shortcuts import render

from accounts.decorators import role_required
from accounts.models import User
from academics.models import Departement, Enseignant, Etudiant, Faculte, Filiere
from pedagogy.models import Cours, RenduDevoir, TravailDirige, TravailPratique


@login_required
@role_required(User.Role.ADMIN)
def statistiques(request):
    stats = {
        'etudiants_par_faculte': list(
            Etudiant.objects.values('filiere__departement__faculte__nom')
            .annotate(total=Count('id')).order_by('-total')
        ),
        'etudiants_par_niveau': list(
            Etudiant.objects.values('niveau__code')
            .annotate(total=Count('id')).order_by('niveau__code')
        ),
        'moyennes_rendus': list(
            RenduDevoir.objects.filter(note__isnull=False)
            .values('td__matiere__nom', 'tp__matiere__nom')
            .annotate(moyenne=Avg('note'))[:10]
        ),
        'inscriptions_par_annee': list(
            Etudiant.objects.values('annee_inscription')
            .annotate(total=Count('id')).order_by('annee_inscription')
        ),
    }
    return render(request, 'reports/statistiques.html', {
        'etudiants_par_faculte': json.dumps(stats['etudiants_par_faculte']),
        'etudiants_par_niveau': json.dumps(stats['etudiants_par_niveau']),
        'moyennes_rendus': json.dumps(stats['moyennes_rendus'], default=str),
        'inscriptions_par_annee': json.dumps(stats['inscriptions_par_annee']),
    })


@login_required
@role_required(User.Role.ADMIN)
def export_excel(request):
    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    ws.title = 'Étudiants'
    ws.append(['Matricule', 'Nom', 'Prénom', 'Filière', 'Niveau', 'Année inscription'])
    for e in Etudiant.objects.select_related('user', 'filiere', 'niveau'):
        ws.append([
            e.matricule,
            e.user.last_name,
            e.user.first_name,
            e.filiere.nom,
            e.niveau.code,
            e.annee_inscription,
        ])

    ws2 = wb.create_sheet('Rendus TP-TD')
    ws2.append(['Étudiant', 'Type', 'Devoir', 'Note', 'Date rendu'])
    for r in RenduDevoir.objects.select_related('etudiant__user', 'td', 'tp'):
        ws2.append([
            str(r.etudiant),
            r.type_devoir,
            str(r.devoir),
            float(r.note) if r.note is not None else '',
            r.date_rendu.strftime('%d/%m/%Y'),
        ])

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    response = HttpResponse(
        buffer.read(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = f'attachment; filename="rapport_universitaire_{datetime.now():%Y%m%d}.xlsx"'
    return response


@login_required
@role_required(User.Role.ADMIN)
def export_pdf(request):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph('Rapport Statistique - Plateforme Universitaire Mauritanienne', styles['Title']))
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f'Généré le {datetime.now():%d/%m/%Y à %H:%M}', styles['Normal']))
    elements.append(Spacer(1, 20))

    data = [['Indicateur', 'Valeur']]
    data.append(['Total étudiants', str(Etudiant.objects.count())])
    data.append(['Total enseignants', str(Enseignant.objects.count())])
    data.append(['Total facultés', str(Faculte.objects.count())])
    data.append(['Total départements', str(Departement.objects.count())])
    data.append(['Total filières', str(Filiere.objects.count())])
    data.append(['Total cours', str(Cours.objects.count())])
    data.append(['Total TD', str(TravailDirige.objects.count())])
    data.append(['Total TP', str(TravailPratique.objects.count())])
    data.append(['Total rendus', str(RenduDevoir.objects.count())])
    moyenne = RenduDevoir.objects.filter(note__isnull=False).aggregate(avg=Avg('note'))['avg']
    data.append(['Moyenne rendus TP/TD', f'{moyenne:.2f}' if moyenne else 'N/A'])

    table = Table(data, colWidths=[300, 150])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3a5f')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    response = HttpResponse(buffer.read(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="rapport_{datetime.now():%Y%m%d}.pdf"'
    return response
