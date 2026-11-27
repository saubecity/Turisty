'use strict';
const $ = (selector) => document.querySelector(selector);
const state = {compte: null, page: 1, total: 0, catalogue: [], options: null, criteres: null, inscription: false, lieuxSortie: new Map()};
const money = (value) => new Intl.NumberFormat('fr-CA', {style: 'currency', currency: 'CAD'}).format(value);
const escapeHtml = (value) => String(value ?? '').replace(/[&<>"']/g, (char) => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'}[char]));
const dateText = (value) => value ? new Date(value.slice(0, 10) + 'T12:00:00').toLocaleDateString('fr-CA', {day: 'numeric', month: 'long', year: 'numeric'}) : 'Date à vérifier';
function notice(message, error = false) {
    $('#notice').textContent = message;
    $('#notice').classList.toggle('error', error);
    $('#notice').hidden = false;
}
async function api(path, method = 'GET', data) {
    const headers = {};
    if (data !== undefined) headers['Content-Type'] = 'application/json';
    if (state.compte) headers['X-CSRF-Token'] = state.compte.Csrf;
    let response;
    try {
        response = await fetch('/api' + path, {method, headers, body: data === undefined ? undefined : JSON.stringify(data)});
    } catch {
        throw new Error('Le serveur est inaccessible. Vérifiez qu’il est lancé, puis réessayez.');
    }
    const result = await response.json();
    if (!response.ok) {
        if (response.status === 401) { state.compte = null; renderAccount(); }
        throw new Error(typeof result.detail === 'string' ? result.detail : 'Vérifiez les informations saisies.');
    }
    return result;
}
function run(action) { Promise.resolve().then(action).catch((error) => notice(error.message, true)); }
function bindForm(selector, action) {
    const form = $(selector);
    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const button = form.querySelector('button[type="submit"]');
        const error = form.querySelector('.form-error');
        if (error) error.textContent = '';
        if (button.disabled) return;
        button.disabled = true;
        try { await action(new FormData(form)); }
        catch (reason) { if (error) error.textContent = reason.message; else notice(reason.message, true); }
        finally { button.disabled = false; }
    });
}
function renderAccount() {
    $('#account').innerHTML = state.compte
        ? `<div class="account-name">${escapeHtml(state.compte.NomCompte)}<button id="logout" class="text-button">Se déconnecter</button></div>`
        : '<button id="login-open" class="outline">Se connecter</button>';
    if (state.compte) $('#logout').onclick = () => run(async () => {
        await api('/deconnexion', 'POST'); state.compte = null; renderAccount(); await navigate(); notice('Vous êtes déconnecté.');
    });
    else $('#login-open').onclick = () => $('#auth-dialog').showModal();
}
function requireAccount() {
    if (state.compte) return true;
    $('#auth-dialog').showModal();
    return false;
}
async function navigate() {
    const allowed = ['decouvrir', 'programme', 'sorties', 'sauvegardes'];
    const page = location.hash.slice(1);
    const selected = allowed.includes(page) ? page : 'decouvrir';
    document.querySelectorAll('.page').forEach((section) => { section.hidden = section.id !== selected; });
    document.querySelectorAll('nav a').forEach((link) => link.classList.toggle('active', link.dataset.page === selected));
    if (selected === 'sorties') await loadSorties();
    if (selected === 'sauvegardes') await loadSaved();
}
let catalogueRequest = 0;
async function loadCatalogue() {
    const requestNumber = ++catalogueRequest;
    const params = new URLSearchParams();
    new FormData($('#filters')).forEach((value, key) => { if (value !== '') params.set(key, value); });
    params.set('page', state.page);
    const data = await api('/catalogue?' + params);
    if (requestNumber !== catalogueRequest) return;
    state.total = data.total; state.catalogue = data.items;
    $('#catalogue-count').textContent = data.total + ' attractions à venir ou en cours';
    $('#catalogue-list').innerHTML = data.items.map((lieu) => `<article class="card">
        <div class="card-top"><span>${escapeHtml(lieu.categorie)}</span>${lieu.demonstration ? '<span class="tag">Fictif · démo</span>' : ''}</div>
        <div class="card-body"><h3>${escapeHtml(lieu.nom)}</h3><p>${dateText(lieu.date_debut)}${lieu.date_fin && lieu.date_fin !== lieu.date_debut ? ' au ' + dateText(lieu.date_fin) : ''}</p>
        <p>${escapeHtml(lieu.adresse || 'Adresse non fournie')}</p><div class="card-bottom"><span class="price">${lieu.prix === null ? 'Prix inconnu' : lieu.prix === 0 ? 'Gratuit' : money(lieu.prix)}</span><button class="outline detail" data-id="${escapeHtml(lieu.id_lieu)}">Voir le lieu</button></div></div></article>`).join('') || '<div class="empty">Aucun lieu ne correspond. Essayez d’autres filtres.</div>';
    $('#prev').disabled = state.page <= 1; $('#next').disabled = state.page * 12 >= data.total;
    $('#pagination-label').textContent = `Page ${state.page} sur ${Math.max(1, Math.ceil(data.total / 12))}`;
    document.querySelectorAll('.detail').forEach((button) => button.onclick = () => run(() => openDetail(button.dataset.id)));
}
async function openDetail(id) {
    const lieu = await api('/catalogue/' + encodeURIComponent(id));
    $('#detail-content').innerHTML = `<p class="eyebrow">${escapeHtml(lieu.categorie)}</p><h2>${escapeHtml(lieu.nom)}</h2>
        <p>${dateText(lieu.date_debut)} → ${dateText(lieu.date_fin)}</p><p class="description">${escapeHtml(lieu.description || 'Aucune description disponible.')}</p>
        <p>${escapeHtml(lieu.adresse || 'Adresse non fournie')}</p><p>${lieu.prix === null ? 'Prix à vérifier auprès du lieu.' : lieu.prix === 0 ? 'Activité gratuite.' : money(lieu.prix) + ' par personne.'}</p>
        <p>${lieu.age_precise ? escapeHtml(lieu.tranche_age) : 'Conditions d’âge non précisées par la source.'}</p>
        ${lieu.latitude !== null && lieu.longitude !== null ? `<p class="small">Coordonnées · ${escapeHtml(lieu.latitude)}, ${escapeHtml(lieu.longitude)}</p>` : ''}
        ${lieu.demonstration ? '<p class="hint">Données fictives pour la démonstration du projet.</p>' : ''}<button id="detail-outing">Organiser une sortie ici</button>`;
    $('#detail-outing').onclick = () => { state.lieuxSortie.set(lieu.id_lieu, lieu.nom); $('#detail-dialog').close(); openOuting(lieu.id_lieu); };
    $('#detail-dialog').showModal();
}
function fillOptions(selector, values) {
    const select = $(selector);
    values.forEach((value) => { const option = document.createElement('option'); option.value = value; option.textContent = value; select.append(option); });
}
function renderProgramme(programme) {
    $('#programme-result').innerHTML = `<h2>Votre programme.</h2>${programme.journees.map((jour) => `<div class="jour"><small>Jour ${jour.numero_jour} · ${dateText(jour.date)}</small><h3>${escapeHtml(jour.nom)}</h3><span>${money(jour.cout)} pour ${programme.nb_personnes} personne(s)</span></div>`).join('')}
        <div class="totals"><div><span>Coût des activités</span><strong>${money(programme.cout_total)}</strong></div><div><span>Budget restant</span><strong>${money(programme.budget_restant)}</strong></div></div>
        <button id="save-open">Enregistrer ce séjour</button><p class="hint">Une activité différente par jour. Le prix et la disponibilité sont à confirmer auprès des lieux.</p>`;
    $('#save-open').onclick = () => { if (requireAccount()) $('#save-dialog').showModal(); };
}
async function loadSaved() {
    if (!state.compte) { $('#saved-list').innerHTML = '<div class="empty">Connectez-vous pour retrouver vos séjours.</div>'; return; }
    const items = await api('/programmes');
    $('#saved-list').innerHTML = items.map((programme) => `<article class="panel"><h2>${escapeHtml(programme.Nomprogram)}</h2><p>${dateText(programme.StartDate)} → ${dateText(programme.EndDate)} · ${programme.NbPersonnes} personne(s)</p>
        ${programme.journees.map((jour) => `<div class="jour"><small>${dateText(jour.date)}</small><h3>${escapeHtml(jour.nom)}</h3>${jour.cout === null ? 'Coût historique non enregistré' : money(jour.cout)}</div>`).join('')}
        <div class="totals"><div><span>Coût total</span><strong>${money(programme.CoutTotal)}</strong></div><div><span>Budget restant</span><strong>${money(programme.budget - programme.CoutTotal)}</strong></div></div>
        <button class="text-button delete-programme" data-id="${programme.IdProgram}">Supprimer ce séjour</button></article>`).join('') || '<div class="empty">Aucun séjour enregistré. Préparez votre premier programme dans « Mon séjour ».</div>';
    document.querySelectorAll('.delete-programme').forEach((button) => button.onclick = () => run(async () => {
        if (!window.confirm('Supprimer ce séjour enregistré ?')) return;
        await api('/programmes/' + button.dataset.id, 'DELETE'); await loadSaved(); notice('Séjour supprimé.');
    }));
}
function openOuting(id) {
    if (!requireAccount()) return;
    const select = $('#outing-attraction'); select.replaceChildren();
    for (const [key, name] of state.lieuxSortie) { const option = document.createElement('option'); option.value = key; option.textContent = name; select.append(option); }
    if (id) select.value = id;
    $('#outing-dialog').showModal();
}
async function loadSorties() {
    const items = await api('/sorties');
    $('#sorties-list').innerHTML = items.map((sortie) => `<article class="card"><div class="card-top">Sortie collective</div><div class="card-body"><h3>${escapeHtml(sortie.NameAttraction)}</h3><p>${dateText(sortie.DateHeureSortie)} · ${escapeHtml(sortie.DateHeureSortie.slice(11, 16))}</p><p>Organisée par ${escapeHtml(sortie.NomCompte)}</p><p>${sortie.occupes} / ${sortie.NbPlacesMax} places acceptées</p>
        ${state.compte && sortie.IdCompte === state.compte.IdCompte ? '<span class="tag">Vous organisez cette sortie</span>' : sortie.ma_demande ? `<span class="tag">${escapeHtml(sortie.ma_demande)}</span>` : `<button class="participate" data-id="${sortie.IdSortie}" ${sortie.occupes >= sortie.NbPlacesMax ? 'disabled' : ''}>${sortie.occupes >= sortie.NbPlacesMax ? 'Sortie complète' : 'Demander à participer'}</button>`}</div></article>`).join('') || '<div class="empty">Aucune sortie à venir. Choisissez une attraction et proposez la première.</div>';
    document.querySelectorAll('.participate').forEach((button) => button.onclick = () => run(async () => {
        if (!requireAccount()) return;
        button.disabled = true;
        try { await api('/sorties/' + button.dataset.id + '/demandes', 'POST'); await loadSorties(); notice('Demande envoyée. Elle attend la décision de l’organisateur.'); }
        finally { button.disabled = false; }
    }));
    $('#requests-panel').hidden = !state.compte;
    if (state.compte) {
        const demandes = await api('/demandes');
        $('#requests-list').innerHTML = demandes.map((demande) => `<div class="request"><p><strong>${escapeHtml(demande.NomCompte)}</strong> · ${escapeHtml(demande.NameAttraction)}<br><span class="small">${escapeHtml(demande.StatutDemande)}</span></p>${demande.StatutDemande === 'En attente' ? `<div><button class="decision" data-sortie="${demande.IdSortie}" data-membre="${demande.IdCompte}" data-statut="Acceptée">Accepter</button><button class="outline decision" data-sortie="${demande.IdSortie}" data-membre="${demande.IdCompte}" data-statut="Refusée">Refuser</button></div>` : ''}</div>`).join('') || '<p>Aucune demande reçue pour vos sorties.</p>';
        document.querySelectorAll('.decision').forEach((button) => button.onclick = () => run(async () => {
            await api(`/sorties/${button.dataset.sortie}/demandes/${button.dataset.membre}`, 'PATCH', {statut: button.dataset.statut});
            await loadSorties(); notice('Décision enregistrée.');
        }));
    }
}
document.querySelectorAll('dialog .close').forEach((button) => button.onclick = () => button.closest('dialog').close());
window.addEventListener('hashchange', () => run(navigate));
$('#filters').addEventListener('submit', (event) => { event.preventDefault(); state.page = 1; run(loadCatalogue); });
$('#reset-filters').onclick = () => { $('#filters').reset(); state.page = 1; run(loadCatalogue); };
$('#prev').onclick = () => { state.page--; run(loadCatalogue); };
$('#next').onclick = () => { state.page++; run(loadCatalogue); };
$('#create-outing').onclick = () => {
    state.catalogue.forEach((lieu) => state.lieuxSortie.set(lieu.id_lieu, lieu.nom)); openOuting();
};
$('#toggle-auth').onclick = () => {
    state.inscription = !state.inscription;
    $('#name-label').hidden = !state.inscription;
    $('#auth-form [name="nom"]').required = state.inscription;
    $('#auth-form [name="mot_de_passe"]').minLength = state.inscription ? 10 : 1;
    $('#auth-form [name="mot_de_passe"]').autocomplete = state.inscription ? 'new-password' : 'current-password';
    $('#auth-title').textContent = state.inscription ? 'Votre compte Turisty.' : 'Bienvenue.';
    $('#auth-description').textContent = state.inscription ? 'Utilisez des informations fictives pour cette démonstration. Mot de passe de 10 caractères minimum.' : 'Connectez-vous pour garder vos séjours et rejoindre une sortie.';
    $('#auth-submit').textContent = state.inscription ? 'Créer mon compte' : 'Se connecter';
    $('#toggle-auth').textContent = state.inscription ? 'J’ai déjà un compte' : 'Créer un compte';
    $('#auth-form .form-error').textContent = '';
};
bindForm('#auth-form', async (data) => {
    const infos = {courriel: data.get('courriel'), mot_de_passe: data.get('mot_de_passe')};
    if (state.inscription) await api('/comptes', 'POST', {...infos, nom: data.get('nom')});
    state.compte = await api('/connexion', 'POST', infos); renderAccount(); $('#auth-dialog').close(); $('#auth-form').reset(); await navigate(); notice('Bienvenue, ' + state.compte.NomCompte + '.');
});
bindForm('#programme-form', async (data) => {
    const criteres = {budget_total: Number(data.get('budget_total')), nb_personnes: Number(data.get('nb_personnes')), duree_jours: Number(data.get('duree_jours')), date_debut: data.get('date_debut'), interet: data.get('interet') || null, categorie: data.get('categorie') || null, tranche_age: data.get('tranche_age') || null};
    const programme = await api('/programmes/generer', 'POST', criteres); state.criteres = criteres; renderProgramme(programme);
});
bindForm('#save-form', async (data) => {
    if (!requireAccount()) return;
    const result = await api('/programmes', 'POST', {...state.criteres, nom: data.get('nom')});
    renderProgramme(result.programme); $('#save-dialog').close(); notice('Séjour enregistré. Retrouvez-le dans « Mes séjours ».');
});
bindForm('#outing-form', async (data) => {
    await api('/sorties', 'POST', {id_attraction: Number(data.get('id_attraction')), date_heure: data.get('date_heure'), places: Number(data.get('places'))});
    $('#outing-dialog').close(); location.hash = 'sorties'; await loadSorties(); notice('Votre sortie est publiée.');
});
run(async () => {
    state.options = await api('/catalogue/options');
    for (const selector of ['#filter-categorie', '#programme-categorie']) fillOptions(selector, state.options.categories);
    for (const selector of ['#filter-interet', '#programme-interet']) fillOptions(selector, state.options.interets);
    $('#start-date').min = state.options.date; $('#start-date').value = state.options.date;
    state.compte = (await api('/moi')).compte; renderAccount(); await loadCatalogue(); await navigate();
});
