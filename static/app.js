'use strict';
const $ = id => document.getElementById(id);
let state = {alimentos:[], movimentos:[], resumo:{}}, token = '';
const fmt = n => new Intl.NumberFormat('pt-BR',{maximumFractionDigits:3}).format(n/1000);
const dt = s => s.slice(0,10).split('-').reverse().join('/');
function cell(row, value) { const td=document.createElement('td'); td.textContent=value; row.append(td); return td; }
function render(){
 const ativos=state.alimentos.filter(i=>i.quantidade_mil>0);
 $('total').textContent=ativos.length;
 $('breve').textContent=ativos.filter(i=>i.situacao==='Vence em breve').length;
 $('vencido').textContent=ativos.filter(i=>i.situacao==='Vencido').length;
 const query=$('busca').value.trim().toLocaleLowerCase('pt-BR'), filter=$('filtro').value;
 const itens=state.alimentos.filter(i=>i.nome.toLocaleLowerCase('pt-BR').includes(query)&&(filter==='todos'||(filter==='ativos'?i.quantidade_mil>0:i.situacao===filter)));
 $('estoque').replaceChildren(); $('vazio').hidden=itens.length>0;
 for(const i of itens){
  const row=document.createElement('tr');const name=cell(row,i.nome);const small=document.createElement('small');small.textContent=`${i.categoria} · ${i.local}`;name.append(small);
  cell(row,`${fmt(i.quantidade_mil)} ${i.unidade}`);cell(row,dt(i.validade));
  const badge=document.createElement('span');badge.className='badge'+(i.situacao==='Vencido'?' late':i.situacao==='Vence em breve'?' soon':'');badge.textContent=i.situacao;cell(row,'').append(badge);
  const actions=cell(row,'');const edit=document.createElement('button');edit.textContent='Editar';edit.className='secondary';edit.addEventListener('click',()=>cadastro(i));actions.append(edit);
  if(i.quantidade_mil>0){const move=document.createElement('button');move.textContent='Registrar saída';move.addEventListener('click',()=>movimento(i));actions.append(move);}
  $('estoque').append(row);
 }
 $('resumo').replaceChildren();for(const [u,v] of Object.entries(state.resumo)){const row=document.createElement('tr');cell(row,u);cell(row,fmt(v.consumo));cell(row,fmt(v.desperdicio));$('resumo').append(row);}
 $('ajustes').replaceChildren();$('sem-ajustes').hidden=(state.ajustes||[]).length>0;
 for(const a of state.ajustes||[]){const row=document.createElement('tr');cell(row,dt(a.criado_em));cell(row,a.nome);cell(row,`${fmt(a.quantidade_anterior_mil)} ${a.unidade_anterior}`);cell(row,`${fmt(a.quantidade_nova_mil)} ${a.unidade_nova}`);$('ajustes').append(row);}
 $('historico').replaceChildren();$('sem-historico').hidden=state.movimentos.length>0;
 for(const m of state.movimentos){const row=document.createElement('tr');cell(row,dt(m.criado_em));cell(row,m.nome);cell(row,m.tipo==='consumo'?'Consumo':'Desperdício');cell(row,`${fmt(m.quantidade_mil)} ${m.unidade}`);cell(row,m.motivo||'—');$('historico').append(row);}
}
async function carregar(){const response=await fetch('/api/painel');if(!response.ok)throw new Error('Não foi possível carregar os dados. Verifique se o servidor está aberto.');state=await response.json();token=state.token;render();}
function cadastro(item){const form=$('form-cadastro');form.reset();form.elements.id.value=item?item.id:'';form.elements.quantidade.disabled=false;form.elements.unidade.disabled=false;form.elements.quantidade.min=item?'0':'0.001';form.dataset.saldo=item?String(item.quantidade_mil):'';form.dataset.unidade=item?item.unidade:'';$('aviso-edicao').hidden=!item;$('erro-cadastro').textContent='';$('titulo-cadastro').textContent=item?'Editar alimento':'Cadastrar alimento';if(item)for(const k of ['nome','categoria','local','unidade','validade'])form.elements[k].value=item[k];if(item)form.elements.quantidade.value=item.quantidade_mil/1000;$('cadastro').showModal();}
function syncMotivo(){const needed=$('tipo').value==='desperdicio';$('motivo-label').hidden=!needed;$('form-movimento').elements.motivo.required=needed;}
function movimento(item){const form=$('form-movimento');form.reset();form.elements.id.value=item.id;form.elements.quantidade.max=item.quantidade_mil/1000;$('item-movimento').textContent=`${item.nome}: disponível ${fmt(item.quantidade_mil)} ${item.unidade}`;$('erro-movimento').textContent='';syncMotivo();$('movimento').showModal();}
async function salvar(event, kind){event.preventDefault();const form=event.target, data=Object.fromEntries(new FormData(form));const button=form.querySelector('[type=submit]');const error=$('erro-'+kind);error.textContent='';button.disabled=true;
 try{let url='/api/alimentos';if(kind==='movimento')url+=`/${data.id}/movimentar`;else if(data.id){url+=`/${data.id}/editar`;data.unidade=form.elements.unidade.value;data.quantidade_anterior_mil=form.dataset.saldo;data.unidade_anterior=form.dataset.unidade;}
 const response=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json','X-CSRF-Token':token},body:JSON.stringify(data)});const result=await response.json();if(!response.ok)throw new Error(result.erro||'Não foi possível salvar.');
 $(kind).close();$('mensagem').textContent='Registro salvo.';
 try{await carregar();}catch(e){$('mensagem').textContent='Registro salvo, mas a atualização da tela falhou. Recarregue a página antes de registrar novamente.';}
 }catch(e){error.textContent=e.message||'Falha de conexão. Verifique o terminal.';}finally{button.disabled=false;}}
$('novo').addEventListener('click',()=>cadastro());$('busca').addEventListener('input',render);$('filtro').addEventListener('change',render);$('tipo').addEventListener('change',syncMotivo);
document.querySelectorAll('[data-close]').forEach(button=>button.addEventListener('click',()=>$(button.dataset.close).close()));
$('form-cadastro').addEventListener('submit',e=>salvar(e,'cadastro'));$('form-movimento').addEventListener('submit',e=>salvar(e,'movimento'));
carregar().catch(e=>{$('mensagem').textContent=e.message;});

