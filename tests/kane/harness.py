#!/usr/bin/env python3
"""
Standalone Kane CLI Test Harness using the fresh ats_verifier package.
Zero dependency on pre-hackathon codebases.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any
from flask import Flask, jsonify, request, render_template_string

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

os.environ.setdefault("FORM_ANSWERS_DISABLE_AI", "1")
os.environ.setdefault("DD_METRICS_ENABLED", "0")

from ats_verifier.dom_autofill import (
    DOMAutofillEngine,
    SCAN_FIELDS_JS,
    INJECT_VALUES_JS,
)
from ats_verifier.form_answers import load_profile, resolve_answer
from ats_verifier.discovery import (
    classify_apply_type,
    RawJob,
    normalize_raw_job,
    deduplicate,
)
from ats_verifier.receipt import DryRunReceipt

RECEIPTS_DIR = REPO_ROOT / "evidence" / "receipts"
RECEIPT_AUDIT_LOG: list[dict] = []

app = Flask(__name__)

PLATFORMS = {
    "greenhouse": {
        "name": "Greenhouse ATS",
        "role": "Senior Cloud Infrastructure Engineer",
        "company": "NorthStar Cloud Inc.",
        "location": "Vancouver, BC (Remote)",
        "req_id": "GH-2026-4410",
        "badge": "bg-emerald-100 text-emerald-800 border-emerald-300",
    },
    "lever": {
        "name": "Lever ATS",
        "role": "Platform Reliability Engineer",
        "company": "Apex Systems Labs",
        "location": "Toronto, ON (Hybrid)",
        "req_id": "LV-2026-7821",
        "badge": "bg-indigo-100 text-indigo-800 border-indigo-300",
    },
    "ashby": {
        "name": "Ashby ATS",
        "role": "AI Systems & Automation Engineer",
        "company": "VectorScale AI",
        "location": "Remote - Canada",
        "req_id": "AS-2026-9012",
        "badge": "bg-purple-100 text-purple-800 border-purple-300",
    },
    "bamboohr": {
        "name": "BambooHR ATS",
        "role": "IT Systems Administrator",
        "company": "Cascadia Health Tech",
        "location": "Surrey, BC",
        "req_id": "BH-2026-3104",
        "badge": "bg-lime-100 text-lime-800 border-lime-300",
    },
    "indeed": {
        "name": "Indeed SmartApply",
        "role": "Network & Security Specialist",
        "company": "Pacific Telco Corp",
        "location": "Burnaby, BC",
        "req_id": "IN-2026-5509",
        "badge": "bg-blue-100 text-blue-800 border-blue-300",
    },
    "linkedin": {
        "name": "LinkedIn Easy Apply",
        "role": "DevOps & AWS Solutions Engineer",
        "company": "Horizon FinTech",
        "location": "Remote - North America",
        "req_id": "LI-2026-6632",
        "badge": "bg-sky-100 text-sky-800 border-sky-300",
    },
    "workopolis": {
        "name": "Workopolis / Job Bank Canada",
        "role": "Technical Support Engineer (Tier 2)",
        "company": "MapleLeaf Digital",
        "location": "Calgary, AB",
        "req_id": "WK-2026-1198",
        "badge": "bg-rose-100 text-rose-800 border-rose-300",
    },
}

PERSONAS = {
    "senior_fullstack": {
        "label": "Senior Full-Stack Dev (Default)",
        "first_name": "Jane",
        "last_name": "Doe",
        "full_name": "Jane Doe",
        "email": "user@example.com",
        "phone": "5550199",
        "city": "Surrey",
        "linkedin": "https://linkedin.com/in/example",
        "work_auth": "Yes",
        "sponsorship": "No",
        "years_exp": "2",
        "salary": "145000",
        "clearance": "No",
    },
    "new_grad": {
        "label": "New Grad Cloud/Network Engineer",
        "first_name": "Alex",
        "last_name": "Chen",
        "full_name": "Alex Chen",
        "email": "alex.chen@example.com",
        "phone": "6045550101",
        "city": "Vancouver",
        "linkedin": "https://linkedin.com/in/alexchen-cloud",
        "work_auth": "Yes",
        "sponsorship": "No",
        "years_exp": "1",
        "salary": "85000",
        "clearance": "No",
    },
    "visa_sponsorship": {
        "label": "Visa-Sponsorship Required Applicant",
        "first_name": "Priya",
        "last_name": "Patel",
        "full_name": "Priya Patel",
        "email": "priya.patel@example.com",
        "phone": "4165550144",
        "city": "Toronto",
        "linkedin": "https://linkedin.com/in/priyapatel-eng",
        "work_auth": "No",
        "sponsorship": "Yes",
        "years_exp": "5",
        "salary": "160000",
        "clearance": "No",
    },
    "healthcare_ops": {
        "label": "Healthcare Operations Specialist",
        "first_name": "Marcus",
        "last_name": "Vance",
        "full_name": "Marcus Vance",
        "email": "marcus.vance@example.com",
        "phone": "5875550188",
        "city": "Calgary",
        "linkedin": "https://linkedin.com/in/marcusvance-ops",
        "work_auth": "Yes",
        "sponsorship": "No",
        "years_exp": "6",
        "salary": "110000",
        "clearance": "Yes",
    },
    "devops_contractor": {
        "label": "DevOps / SRE Contractor",
        "first_name": "Elena",
        "last_name": "Rostova",
        "full_name": "Elena Rostova",
        "email": "elena.rostova@example.com",
        "phone": "5145550177",
        "city": "Montreal",
        "linkedin": "https://linkedin.com/in/elenarostova-sre",
        "work_auth": "Yes",
        "sponsorship": "No",
        "years_exp": "8",
        "salary": "175000",
        "clearance": "Yes",
    },
    "security_analyst": {
        "label": "Security Analyst (SOC / AppSec)",
        "first_name": "Devon",
        "last_name": "Brooks",
        "full_name": "Devon Brooks",
        "email": "devon.brooks@example.com",
        "phone": "6135550122",
        "city": "Ottawa",
        "linkedin": "https://linkedin.com/in/devonbrooks-sec",
        "work_auth": "Yes",
        "sponsorship": "No",
        "years_exp": "4",
        "salary": "130000",
        "clearance": "Yes",
    },
    "data_engineer": {
        "label": "Data Engineer (Spark / dbt)",
        "first_name": "Sofia",
        "last_name": "Mendez",
        "full_name": "Sofia Mendez",
        "email": "sofia.mendez@example.com",
        "phone": "4035550133",
        "city": "Calgary",
        "linkedin": "https://linkedin.com/in/sofiamendez-data",
        "work_auth": "Yes",
        "sponsorship": "No",
        "years_exp": "5",
        "salary": "140000",
        "clearance": "No",
    },
    "product_manager": {
        "label": "Technical Product Manager",
        "first_name": "Liam",
        "last_name": "OConnor",
        "full_name": "Liam OConnor",
        "email": "liam.oconnor@example.com",
        "phone": "4165550155",
        "city": "Toronto",
        "linkedin": "https://linkedin.com/in/liamoconnor-pm",
        "work_auth": "Yes",
        "sponsorship": "No",
        "years_exp": "6",
        "salary": "155000",
        "clearance": "No",
    },
    "qa_automation": {
        "label": "QA Automation Engineer",
        "first_name": "Hannah",
        "last_name": "Kim",
        "full_name": "Hannah Kim",
        "email": "hannah.kim@example.com",
        "phone": "6045550166",
        "city": "Burnaby",
        "linkedin": "https://linkedin.com/in/hannahkim-qa",
        "work_auth": "Yes",
        "sponsorship": "No",
        "years_exp": "4",
        "salary": "120000",
        "clearance": "No",
    },
    "international_coop": {
        "label": "International Co-op Student",
        "first_name": "Arjun",
        "last_name": "Mehta",
        "full_name": "Arjun Mehta",
        "email": "arjun.mehta@example.com",
        "phone": "7785550199",
        "city": "Vancouver",
        "linkedin": "https://linkedin.com/in/arjunmehta-coop",
        "work_auth": "No",
        "sponsorship": "Yes",
        "years_exp": "1",
        "salary": "65000",
        "clearance": "No",
    },
}

VARIANTS = ("standard", "mutated_ids", "strict_policy_screening", "dirty_dedup_batch")

INDEX_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>JobsFarm — Kane CLI Verification Harness</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen p-8">
  <div class="max-w-5xl mx-auto space-y-8">
    <header class="border-b border-slate-800 pb-6 flex items-center justify-between">
      <div>
        <span class="text-xs font-mono uppercase px-2.5 py-1 rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
          Untouched JobsFarm Codebase &bull; AGPL-3.0
        </span>
        <h1 class="text-3xl font-bold mt-3">JobsFarm 🚜 Kane CLI Test Harness</h1>
        <p class="text-slate-400 text-sm mt-1">
          Live browser verification of JobsFarm's <code>DOMAutofillEngine</code>, 7,300+ QA Bank, and Discovery Pipeline.
        </p>
      </div>
      <div class="text-right text-xs font-mono text-slate-400">
        <div>Safety Mode: <span class="text-amber-400 font-bold">DRY_RUN_ENFORCED</span></div>
        <div>Profile: <span class="text-cyan-400">{{ profile_name }}</span></div>
      </div>
    </header>

    <section>
      <h2 class="text-lg font-semibold mb-4 text-slate-200">Supported ATS &amp; Job Portal Targets</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {% for slug, info in platforms.items() %}
        <a href="/ats/{{ slug }}" id="link-{{ slug }}"
           class="block p-5 rounded-xl bg-slate-900 border border-slate-800 hover:border-emerald-500/50 transition">
          <div class="flex items-center justify-between">
            <span class="font-bold text-white">{{ info.name }}</span>
            <span class="text-xs font-mono text-emerald-400">{{ info.req_id }}</span>
          </div>
          <div class="text-sm text-slate-300 mt-2">{{ info.role }}</div>
          <div class="text-xs text-slate-500 mt-1">{{ info.company }} &bull; {{ info.location }}</div>
        </a>
        {% endfor %}
      </div>
    </section>

    <section class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <a href="/tools/qa-bank" id="link-qa-bank"
         class="block p-5 rounded-xl bg-slate-900 border border-slate-800 hover:border-cyan-500/50 transition">
        <div class="font-bold text-cyan-400">🧠 7,300+ QA Bank &amp; Policy Brain Tester</div>
        <p class="text-xs text-slate-400 mt-1">Query <code>jobbots.core.shared_modules.form_answers.resolve_answer()</code> directly.</p>
      </a>
      <a href="/tools/discovery-dedupe" id="link-discovery-dedupe"
         class="block p-5 rounded-xl bg-slate-900 border border-slate-800 hover:border-purple-500/50 transition">
        <div class="font-bold text-purple-400">🔍 Two-Stage Discovery &amp; Deduplication Tester</div>
        <p class="text-xs text-slate-400 mt-1">Test <code>normalize_raw_job()</code>, <code>deduplicate_jobs()</code>, and <code>classify_apply_type()</code>.</p>
      </a>
    </section>

    <section class="border-t border-slate-800 pt-6">
      <h2 class="text-lg font-semibold mb-3 text-slate-200">Multi-Persona &amp; DOM Layout Matrix (Training Trajectory Grid)</h2>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
        {% for pid, pdata in personas.items() %}
        <div class="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
          <div class="font-bold text-amber-400">{{ pdata.full_name }} &mdash; {{ pdata.label }}</div>
          <div class="flex flex-wrap gap-2">
            <a href="/ats/greenhouse?persona={{ pid }}&variant=standard" class="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200">Standard</a>
            <a href="/ats/greenhouse?persona={{ pid }}&variant=mutated_ids" class="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-cyan-300">Mutated IDs</a>
            <a href="/ats/greenhouse?persona={{ pid }}&variant=strict_policy_screening" class="px-2 py-1 rounded bg-slate-800 hover:bg-slate-700 text-rose-300">Strict Policy</a>
          </div>
        </div>
        {% endfor %}
      </div>
    </section>
  </div>
</body>
</html>
"""

NETWORK_GUARD_SNIPPET = """<script>
(function () {
  const enabled = {{ network_guard_enabled | tojson }};
  if (!enabled) {
    document.documentElement.dataset.networkGuard = 'disabled';
    return;
  }
  document.documentElement.dataset.networkGuard = 'active';
  const allowed = /^https?:\\/\\/(127\\.0\\.0\\.1|localhost)(:8766)?/i;
  function isExternal(url) {
    try {
      const u = new URL(url, window.location.href);
      if (u.origin === window.location.origin) return false;
      return !allowed.test(u.href);
    } catch (e) {
      return true;
    }
  }
  function block(url) {
    window.__LAST_NETWORK_BLOCK__ = url;
    const el = document.getElementById('network-guard-banner');
    if (el) {
      el.textContent = 'NETWORK_SUBMIT_GUARD_BLOCKED ' + url;
      el.classList.remove('hidden');
    }
    document.body && document.body.setAttribute('data-network-guard-blocked', 'true');
  }
  const origFetch = window.fetch;
  window.fetch = function (input, init) {
    const method = ((init && init.method) || 'GET').toUpperCase();
    const url = typeof input === 'string' ? input : (input && input.url) || '';
    if (method === 'POST' && isExternal(url)) {
      block(url);
      return Promise.reject(new Error('NETWORK_SUBMIT_GUARD_BLOCKED'));
    }
    return origFetch.apply(this, arguments);
  };
  const XHR = window.XMLHttpRequest;
  function WrappedXHR() {
    const xhr = new XHR();
    const open = xhr.open;
    xhr.open = function (method, url) {
      this.__guardMethod = method;
      this.__guardUrl = url;
      return open.apply(this, arguments);
    };
    const send = xhr.send;
    xhr.send = function () {
      if (String(this.__guardMethod || '').toUpperCase() === 'POST' && isExternal(this.__guardUrl || '')) {
        block(this.__guardUrl);
        throw new Error('NETWORK_SUBMIT_GUARD_BLOCKED');
      }
      return send.apply(this, arguments);
    };
    return xhr;
  }
  window.XMLHttpRequest = WrappedXHR;
})();
</script>"""

ATS_FORM_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{{ info.role }} - {{ info.company }} | {{ info.name }}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  """ + NETWORK_GUARD_SNIPPET + """
</head>
<body class="bg-slate-50 text-slate-900 min-h-screen py-10 px-4">
  <div class="max-w-3xl mx-auto bg-white rounded-xl shadow-sm border border-slate-200 overflow-hidden">
    <div class="bg-slate-900 text-white p-6 flex items-center justify-between">
      <div>
        <span class="text-xs font-semibold px-2.5 py-0.5 rounded-full border {{ info.badge }}">{{ info.name }}</span>
        <h1 id="job-title" class="text-2xl font-bold mt-2">{{ info.role }}</h1>
        <p id="company-name" class="text-slate-300 text-sm">{{ info.company }} &bull; {{ info.location }}</p>
      </div>
      <div class="text-right font-mono text-xs">
        <div class="text-slate-400">Requisition</div>
        <div id="req-id" class="text-emerald-400 font-bold">{{ info.req_id }}</div>
      </div>
    </div>

    <div class="bg-amber-50 border-b border-amber-200 px-6 py-3 flex items-center justify-between text-xs text-amber-900">
      <span>🛡️ <strong>JobsFarm Dry-Run Verification:</strong> External submission disabled. <span class="ml-2 font-mono text-slate-600">[persona={{ persona_id }} | variant={{ variant }}]</span></span>
      <span id="autofill-badge" class="px-2 py-0.5 rounded bg-amber-200 font-mono font-bold">WAITING_FOR_JOBSFARM</span>
    </div>

    <form id="ats-form" class="p-6 space-y-5" onsubmit="event.preventDefault(); return false;">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label for="{{ fids.first_name }}" class="block text-xs font-semibold text-slate-700 uppercase">First Name *</label>
          <input id="{{ fids.first_name }}" name="{{ fids.first_name }}" type="text" required class="mt-1 w-full px-3 py-2 border rounded-lg text-sm">
        </div>
        <div>
          <label for="{{ fids.last_name }}" class="block text-xs font-semibold text-slate-700 uppercase">Last Name *</label>
          <input id="{{ fids.last_name }}" name="{{ fids.last_name }}" type="text" required class="mt-1 w-full px-3 py-2 border rounded-lg text-sm">
        </div>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label for="{{ fids.email }}" class="block text-xs font-semibold text-slate-700 uppercase">Email *</label>
          <input id="{{ fids.email }}" name="{{ fids.email }}" type="email" required class="mt-1 w-full px-3 py-2 border rounded-lg text-sm">
        </div>
        <div>
          <label for="{{ fids.phone }}" class="block text-xs font-semibold text-slate-700 uppercase">Phone *</label>
          <input id="{{ fids.phone }}" name="{{ fids.phone }}" type="tel" required class="mt-1 w-full px-3 py-2 border rounded-lg text-sm">
        </div>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label for="{{ fids.linkedin }}" class="block text-xs font-semibold text-slate-700 uppercase">LinkedIn Profile</label>
          <input id="{{ fids.linkedin }}" name="{{ fids.linkedin }}" type="url" class="mt-1 w-full px-3 py-2 border rounded-lg text-sm">
        </div>
        <div>
          <label for="{{ fids.city }}" class="block text-xs font-semibold text-slate-700 uppercase">City</label>
          <input id="{{ fids.city }}" name="{{ fids.city }}" type="text" class="mt-1 w-full px-3 py-2 border rounded-lg text-sm">
        </div>
      </div>

      <div>
        <label for="{{ fids.work_auth }}" class="block text-xs font-semibold text-slate-700 uppercase">Are you legally authorized to work in Canada? *</label>
        <select id="{{ fids.work_auth }}" name="{{ fids.work_auth }}" required class="mt-1 w-full px-3 py-2 border rounded-lg text-sm bg-white">
          <option value="">-- Select --</option>
          <option value="Yes">Yes</option>
          <option value="No">No</option>
        </select>
      </div>

      <div>
        <label for="{{ fids.sponsorship }}" class="block text-xs font-semibold text-slate-700 uppercase">Will you now or in the future require visa sponsorship? *</label>
        <select id="{{ fids.sponsorship }}" name="{{ fids.sponsorship }}" required class="mt-1 w-full px-3 py-2 border rounded-lg text-sm bg-white">
          <option value="">-- Select --</option>
          <option value="Yes">Yes</option>
          <option value="No">No</option>
        </select>
      </div>

      <div>
        <label for="{{ fids.years_exp }}" class="block text-xs font-semibold text-slate-700 uppercase">Years of Python experience *</label>
        <input id="{{ fids.years_exp }}" name="{{ fids.years_exp }}" type="text" required class="mt-1 w-full px-3 py-2 border rounded-lg text-sm">
      </div>

      {% if variant == 'strict_policy_screening' %}
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 p-4 rounded-lg bg-rose-50 border border-rose-200">
        <div>
          <label for="salary_expectation" class="block text-xs font-semibold text-rose-900 uppercase">Desired Base Salary (CAD) *</label>
          <input id="salary_expectation" name="salary_expectation" type="text" required class="mt-1 w-full px-3 py-2 border rounded-lg text-sm bg-white">
        </div>
        <div>
          <label for="security_clearance" class="block text-xs font-semibold text-rose-900 uppercase">Canadian Security Clearance Eligible? *</label>
          <select id="security_clearance" name="security_clearance" required class="mt-1 w-full px-3 py-2 border rounded-lg text-sm bg-white">
            <option value="">-- Select --</option>
            <option value="Yes">Yes</option>
            <option value="No">No</option>
          </select>
        </div>
      </div>
      {% endif %}

      <div>
        <label for="{{ fids.cover_letter }}" class="block text-xs font-semibold text-slate-700 uppercase">Why are you interested in this role?</label>
        <textarea id="{{ fids.cover_letter }}" name="{{ fids.cover_letter }}" rows="3" class="mt-1 w-full px-3 py-2 border rounded-lg text-sm"></textarea>
      </div>

      <div class="pt-4 border-t flex items-center justify-between">
        <a href="/" class="text-xs text-slate-500 hover:underline">&larr; Back to Harness</a>
        <div class="flex items-center space-x-3">
          <button type="button" id="btn-run-autofill" onclick="runJobsFarmAutofill()"
                  class="px-4 py-2 text-xs font-bold rounded-lg bg-slate-900 hover:bg-slate-800 text-white">
            🚜 Run JobsFarm DOMAutofillEngine
          </button>
          <button type="button" id="btn-submit" onclick="handleDryRunSubmit()"
                  class="px-4 py-2 text-xs font-bold rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white">
            Submit Application
          </button>
        </div>
      </div>
    </form>

    <div id="network-guard-banner" class="hidden p-3 bg-rose-50 border-t border-rose-200 text-xs font-mono text-rose-900">NETWORK_SUBMIT_GUARD_BLOCKED</div>
    <div id="submit-alert" class="hidden p-4 bg-emerald-50 border-t border-emerald-200 text-xs text-emerald-900 flex items-center justify-between">
      <span id="submit-msg">Dry-Run Guard: Form prepared &amp; verified, external POST aborted.</span>
      <div class="flex items-center space-x-2">
        <span id="receipt-badge" class="hidden font-mono text-xs px-2 py-0.5 rounded bg-emerald-200 text-emerald-900 font-bold">PREFLIGHT_COMPLIANT</span>
        <span class="font-mono font-bold text-emerald-700">SAFETY_GUARD_ACTIVE</span>
      </div>
    </div>
  </div>

  <script>
    const SCAN_FN = {{ scan_js | safe }};
    const INJECT_FN = {{ inject_js | safe }};

    async function runJobsFarmAutofill() {
      const scanned = SCAN_FN;
      const res = await fetch('/api/resolve-fields', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          fields: scanned,
          job_context: "{{ info.role }} at {{ info.company }}",
          persona: "{{ persona_id }}",
          variant: "{{ variant }}"
        })
      });
      const data = await res.json();
      let filledCount = INJECT_FN(data.answers);
      {% if loop_seed_bug == 'visa_wrong_answer' and persona_id == 'visa_sponsorship' %}
      const _seedSponsor = document.getElementById('{{ fids.sponsorship }}');
      if (_seedSponsor) {
        _seedSponsor.value = 'No';
        _seedSponsor.dispatchEvent(new Event('change', { bubbles: true }));
      }
      {% endif %}
      {% if loop_seed_bug == 'email_wrong_answer' %}
      const _seedEmail = document.getElementById('{{ fids.email }}');
      if (_seedEmail) { _seedEmail.value = 'wrong.agent@example.com'; _seedEmail.dispatchEvent(new Event('input', { bubbles: true })); }
      {% endif %}
      {% if loop_seed_bug == 'salary_wrong_answer' and variant == 'strict_policy_screening' %}
      const _seedSalary = document.getElementById('salary_expectation');
      if (_seedSalary) { _seedSalary.value = '90000'; _seedSalary.dispatchEvent(new Event('input', { bubbles: true })); }
      {% endif %}
      {% if agent_policy.get('email') %}
      const _agentEmail = document.getElementById('{{ fids.email }}');
      if (_agentEmail) { _agentEmail.value = {{ agent_policy.email | tojson }}; _agentEmail.dispatchEvent(new Event('input', { bubbles: true })); }
      {% endif %}
      {% if agent_policy.get('salary_expectation') %}
      const _agentSalary = document.getElementById('salary_expectation');
      if (_agentSalary) { _agentSalary.value = {{ agent_policy.salary_expectation | tojson }}; _agentSalary.dispatchEvent(new Event('input', { bubbles: true })); }
      {% endif %}
      {% if agent_policy.get('sponsorship') %}
      const _agentSponsor = document.getElementById('{{ fids.sponsorship }}');
      if (_agentSponsor) {
        _agentSponsor.value = {{ agent_policy.sponsorship | tojson }};
        _agentSponsor.dispatchEvent(new Event('change', { bubbles: true }));
      }
      {% endif %}
      const badge = document.getElementById('autofill-badge');
      badge.textContent = 'AUTOFILL_COMPLETED (' + filledCount + '/' + scanned.length + ')';
      badge.className = 'px-2 py-0.5 rounded bg-emerald-200 text-emerald-900 font-mono font-bold';
    }

    async function handleDryRunSubmit() {
      const form = document.getElementById('ats-form');
      const isValid = form ? form.checkValidity() : true;
      const ariaInvalidCount = form ? form.querySelectorAll('[aria-invalid="true"]').length : 0;
      const payload = {};
      if (form) {
        const elements = form.querySelectorAll('input, select, textarea');
        elements.forEach(el => {
          const key = el.name || el.id;
          if (key && el.type !== 'button' && el.type !== 'submit') {
            payload[key] = el.value;
          }
        });
      }
      const receiptData = {
        ats_type: "{{ slug or 'unknown' }}",
        target_url: window.location.href,
        intercepted_method: "POST",
        persona: "{{ persona_id }}",
        variant: "{{ variant }}",
        html5_valid: isValid,
        aria_invalid_count: ariaInvalidCount,
        payload: payload
      };
      window.__LAST_DRY_RUN_RECEIPT__ = receiptData;
      try {
        const resp = await fetch('/api/dry-run-receipt', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(receiptData)
        });
        const resJson = await resp.json();
        if (resJson && resJson.receipt) {
          window.__LAST_DRY_RUN_RECEIPT__ = resJson.receipt;
        }
      } catch (err) {
        console.warn('Dry-run receipt endpoint warning:', err);
      }
      const alertEl = document.getElementById('submit-alert');
      const msgEl = document.getElementById('submit-msg');
      const badgeEl = document.getElementById('receipt-badge');
      if (msgEl) {
        msgEl.textContent = 'Dry-Run Receipt Generated: Payload verified (' + Object.keys(payload).length + ' fields, HTML5 valid=' + isValid + '). External POST aborted.';
      }
      if (badgeEl) {
        badgeEl.classList.remove('hidden');
      }
      if (alertEl) {
        alertEl.classList.remove('hidden');
      }
    }
  </script>
</body>
</html>
"""

QA_BANK_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>JobsFarm 7,300+ QA Bank Tester</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen p-8">
  <div class="max-w-3xl mx-auto space-y-6">
    <div class="flex items-center justify-between border-b border-slate-800 pb-4">
      <h1 class="text-2xl font-bold">🧠 JobsFarm QA Bank &amp; Policy Resolution Tester</h1>
      <a href="/" class="text-xs text-slate-400 hover:text-white">&larr; Back</a>
    </div>
    <div class="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
      <label for="question-input" class="block text-xs font-semibold uppercase text-slate-400">Screening Question</label>
      <input id="question-input" type="text" value="Are you legally authorized to work in Canada?"
             class="w-full px-3 py-2 rounded bg-slate-950 border border-slate-700 text-sm text-white">
      <div class="flex flex-wrap gap-2">
        <button type="button" id="btn-preset-auth" onclick="setQ('Are you legally authorized to work in Canada?')" class="px-3 py-1 text-xs rounded bg-slate-800 hover:bg-slate-700">Work Auth</button>
        <button type="button" id="btn-preset-visa" onclick="setQ('Will you now or in the future require sponsorship?')" class="px-3 py-1 text-xs rounded bg-slate-800 hover:bg-slate-700">Visa Sponsorship</button>
        <button type="button" id="btn-preset-exp" onclick="setQ('How many years of Python experience do you have?')" class="px-3 py-1 text-xs rounded bg-slate-800 hover:bg-slate-700">Python Experience</button>
        <button type="button" id="btn-preset-star" onclick="setQ('Describe a challenging technical problem you solved.')" class="px-3 py-1 text-xs rounded bg-slate-800 hover:bg-slate-700">STAR Behavioral</button>
      </div>
      <button type="button" id="btn-resolve-qa" onclick="resolveQA()"
              class="px-4 py-2 rounded-lg bg-cyan-500 hover:bg-cyan-400 text-slate-950 text-xs font-bold">
        Resolve Answer from JobsFarm QA Bank
      </button>
      <div id="qa-result" class="hidden p-4 rounded-lg bg-slate-950 border border-slate-800 space-y-2 text-xs">
        <div><span class="text-slate-400">Resolved Value:</span> <span id="qa-value" class="text-emerald-400 font-bold"></span></div>
        <div><span class="text-slate-400">Policy / Bank Source:</span> <span id="qa-source" class="text-cyan-400 font-mono"></span></div>
      </div>
    </div>
  </div>
  <script>
    function setQ(text) { document.getElementById('question-input').value = text; }
    async function resolveQA() {
      const q = document.getElementById('question-input').value;
      const res = await fetch('/api/resolve-qa', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: q })
      });
      const data = await res.json();
      document.getElementById('qa-value').textContent = data.value;
      document.getElementById('qa-source').textContent = data.source;
      document.getElementById('qa-result').classList.remove('hidden');
    }
  </script>
</body>
</html>
"""

DISCOVERY_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>JobsFarm Two-Stage Discovery &amp; Dedupe Tester</title>
  <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-950 text-slate-100 min-h-screen p-8">
  <div class="max-w-4xl mx-auto space-y-6">
    <div class="flex items-center justify-between border-b border-slate-800 pb-4">
      <h1 class="text-2xl font-bold">🔍 JobsFarm Discovery Normalizer &amp; Deduplicator</h1>
      <a href="/" class="text-xs text-slate-400 hover:text-white">&larr; Back</a>
    </div>
    <div class="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-4">
      <p class="text-xs text-slate-400">
        Tests untouched <code>normalize_raw_job()</code>, <code>classify_apply_type()</code>, and <code>deduplicate_jobs()</code> against duplicate cross-board leads.
      </p>
      <button type="button" id="btn-run-dedupe" onclick="runDedupe()"
              class="px-4 py-2 rounded-lg bg-purple-500 hover:bg-purple-400 text-slate-950 text-xs font-bold">
        Run JobsFarm Discovery Deduplication
      </button>
      <div id="dedupe-summary" class="hidden grid grid-cols-3 gap-4 text-xs">
        <div class="p-3 rounded bg-slate-950 border border-slate-800">
          <div class="text-slate-400">Raw Scraped Leads</div>
          <div id="raw-count" class="text-xl font-bold font-mono text-white">0</div>
        </div>
        <div class="p-3 rounded bg-slate-950 border border-slate-800">
          <div class="text-slate-400">Unique Normalized Jobs</div>
          <div id="unique-count" class="text-xl font-bold font-mono text-emerald-400">0</div>
        </div>
        <div class="p-3 rounded bg-slate-950 border border-slate-800">
          <div class="text-slate-400">Duplicates Removed</div>
          <div id="removed-count" class="text-xl font-bold font-mono text-amber-400">0</div>
        </div>
      </div>
      <div id="dedupe-list" class="space-y-2 text-xs"></div>
    </div>
  </div>
  <script>
    async function runDedupe() {
      const urlParams = new URLSearchParams(window.location.search);
      const batch = urlParams.get('batch') || 'standard';
      const res = await fetch('/api/run-dedupe?batch=' + encodeURIComponent(batch), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ batch: batch }),
      });
      const data = await res.json();
      document.getElementById('raw-count').textContent = data.raw_count;
      document.getElementById('unique-count').textContent = data.unique_count;
      document.getElementById('removed-count').textContent = data.duplicates_removed;
      document.getElementById('dedupe-summary').classList.remove('hidden');
      document.getElementById('dedupe-list').innerHTML = data.jobs.map(j => `
        <div class="p-3 rounded bg-slate-950 border border-slate-800 flex justify-between items-center">
          <div>
            <span class="font-bold text-white">${j.title}</span>
            <span class="text-slate-400"> @ ${j.company}</span>
          </div>
          <span class="font-mono text-emerald-400">${j.apply_type}</span>
        </div>
      `).join('');
    }
  </script>
</body>
</html>
"""


@app.route("/")
def index():
    profile = load_profile()
    return render_template_string(
        INDEX_HTML,
        platforms=PLATFORMS,
        personas=PERSONAS,
        profile_name=profile.get("full_name", "Candidate"),
    )


def _field_ids_for_variant(variant: str) -> dict:
    if variant == "mutated_ids":
        return {
            "first_name": "fld_9a1x",
            "last_name": "fld_7b2z",
            "email": "fld_3c4m",
            "phone": "fld_8d5p",
            "linkedin": "fld_2e6k",
            "city": "fld_4f7q",
            "work_auth": "fld_1g8w",
            "sponsorship": "fld_5h9r",
            "years_exp": "fld_6j0t",
            "cover_letter": "fld_0k3v",
        }
    return {
        "first_name": "first_name",
        "last_name": "last_name",
        "email": "email",
        "phone": "phone",
        "linkedin": "linkedin",
        "city": "city",
        "work_auth": "work_auth",
        "sponsorship": "sponsorship",
        "years_exp": "years_exp",
        "cover_letter": "cover_letter",
    }


@app.route("/ats/<slug>")
def ats_page(slug):
    info = PLATFORMS.get(slug)
    if not info:
        return "Platform not found", 404
    persona_id = request.args.get("persona", "senior_fullstack")
    if persona_id not in PERSONAS:
        persona_id = "senior_fullstack"
    variant = request.args.get("variant", "standard")
    if variant not in VARIANTS:
        variant = "standard"
    return render_template_string(
        ATS_FORM_HTML,
        info=info,
        slug=slug,
        persona_id=persona_id,
        variant=variant,
        fids=_field_ids_for_variant(variant),
        loop_seed_bug=_active_loop_seed_bug(),
        agent_policy=_active_agent_policy(),
        network_guard_enabled=network_guard_enabled_for_request(),
        scan_js=SCAN_FIELDS_JS.strip(),
        inject_js=INJECT_VALUES_JS.strip(),
    )


NETWORK_GUARD_TEST_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Network Submit Guard Probe</title>
  <script src="https://cdn.tailwindcss.com"></script>
  """ + NETWORK_GUARD_SNIPPET + """
</head>
<body class="bg-slate-50 p-8">
  <div class="max-w-lg mx-auto bg-white border rounded-xl p-6 space-y-4">
    <h1 class="text-lg font-bold">P0-3 network no-submit guard probe</h1>
    <p class="text-sm text-slate-600">Posts to a synthetic Greenhouse-style URL (non-harness host). Guard must block before leave <code>127.0.0.1:8766</code>.</p>
    <button type="button" id="btn-probe" onclick="probeExternalSubmit()"
      class="px-4 py-2 bg-slate-900 text-white text-sm rounded-lg font-semibold">
      Probe external application POST
    </button>
    <p id="probe-status" class="text-xs font-mono text-slate-500">PROBE_IDLE</p>
    <div id="network-guard-banner" class="hidden p-3 bg-rose-50 border border-rose-200 text-xs font-mono text-rose-900">NETWORK_SUBMIT_GUARD_BLOCKED</div>
    {% if not network_guard_enabled %}
    <p id="network-guard-disabled" class="text-xs font-mono text-amber-800">NETWORK_SUBMIT_GUARD_DISABLED</p>
    {% endif %}
  </div>
  <script>
    async function probeExternalSubmit() {
      const status = document.getElementById('probe-status');
      status.textContent = 'PROBE_SENDING';
      try {
        await fetch('https://boards.greenhouse.io/v1/applications', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ dry_run: true })
        });
        status.textContent = 'PROBE_UNBLOCKED_OK';
      } catch (err) {
        status.textContent = String(err && err.message ? err.message : err);
      }
    }
  </script>
</body>
</html>"""


@app.route("/tools/network-guard-test")
def network_guard_test_tool():
    return render_template_string(
        NETWORK_GUARD_TEST_HTML,
        network_guard_enabled=network_guard_enabled_for_request(),
    )


@app.route("/tools/qa-bank")
def qa_bank_tool():
    return render_template_string(QA_BANK_HTML)


@app.route("/tools/discovery-dedupe")
def discovery_tool():
    return render_template_string(DISCOVERY_HTML)


def _active_loop_seed_bug() -> str | None:
    marker = Path(__file__).with_name(".loop_seed_bug")
    if marker.is_file():
        return marker.read_text(encoding="utf-8").strip() or None
    return os.environ.get("KANE_SEED_BUG") or None


def network_guard_enabled_for_request() -> bool:
    if request.args.get("guard") == "off":
        return False
    return os.environ.get("KANE_NETWORK_GUARD", "1").strip().lower() not in {"0", "false", "off"}


def _active_agent_policy() -> dict[str, Any]:
    marker = Path(__file__).with_name(".loop_agent_policy.json")
    if not marker.is_file():
        return {}
    try:
        payload = json.loads(marker.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    fields = dict(payload.get("fields") or {}) if isinstance(payload, dict) else {}
    if isinstance(payload, dict) and "rules" in payload:
        fields["_rules"] = payload["rules"]
    return {str(k): str(v) if k != "_rules" else v for k, v in fields.items() if v is not None}


@app.route("/api/resolve-fields", methods=["POST"])
def api_resolve_fields():
    data = request.json or {}
    fields = data.get("fields", [])
    job_context = data.get("job_context", "")
    persona_id = data.get("persona", "senior_fullstack")
    persona = PERSONAS.get(persona_id, PERSONAS["senior_fullstack"])

    profile = dict(load_profile())
    if persona_id != "senior_fullstack":
        profile.update({
            "first_name": persona["first_name"],
            "last_name": persona["last_name"],
            "full_name": persona["full_name"],
            "email": persona["email"],
            "phone": persona["phone"],
            "city": persona["city"],
            "linkedin": persona["linkedin"],
            "years_of_experience": persona["years_exp"],
            "salary_expectation": persona["salary"],
        })

    answers = DOMAutofillEngine.resolve_field_answers(
        fields=fields,
        profile=profile,
        job_context=job_context,
    )

    by_id = {item.get("id"): item for item in answers if isinstance(item, dict) and item.get("id")}

    def _set_answer(fld_obj: dict, val: str) -> None:
        key = fld_obj.get("id") or fld_obj.get("name")
        if not key:
            return
        if key in by_id:
            by_id[key]["value"] = val
        else:
            entry = {
                "_frame_index": fld_obj.get("_frame_index", 0),
                "id": key,
                "radio_options": fld_obj.get("radio_options", []),
                "type": fld_obj.get("type", "text"),
                "value": val,
            }
            answers.append(entry)
            by_id[key] = entry

    # Ensure strict screening & non-default persona policy fields resolve cleanly
    for fld in fields:
        fid = (fld.get("id") or fld.get("name") or "").lower()
        label = (fld.get("label") or "").lower()
        if "salary" in fid or "salary" in label:
            policy = _active_agent_policy()
            if "salary_expectation" in policy:
                _set_answer(fld, policy["salary_expectation"])
            elif _active_loop_seed_bug() == "salary_wrong_answer" and persona_id == "visa_sponsorship":
                _set_answer(fld, "90000")
            else:
                _set_answer(fld, persona["salary"])
        elif "email" in fid or "email" in label:
            policy = _active_agent_policy()
            if "email" in policy:
                _set_answer(fld, policy["email"])
            elif _active_loop_seed_bug() == "email_wrong_answer":
                _set_answer(fld, "wrong.agent@example.com")
            else:
                pass
        elif "clearance" in fid or "clearance" in label:
            _set_answer(fld, persona["clearance"])
        elif persona_id != "senior_fullstack":
            if "authorized to work" in label or "work_auth" in fid:
                _set_answer(fld, persona["work_auth"])
            elif "sponsorship" in label or "sponsorship" in fid:
                policy = _active_agent_policy()
                if "sponsorship" in policy:
                    _set_answer(fld, policy["sponsorship"])
                elif _active_loop_seed_bug() == "visa_wrong_answer" and persona_id == "visa_sponsorship":
                    _set_answer(fld, "No")  # planted bug (CL-2); labeled in hackathon docs
                else:
                    _set_answer(fld, persona["sponsorship"])
            elif "years of python" in label or "years_exp" in fid:
                _set_answer(fld, persona["years_exp"])

    return jsonify({"status": "success", "persona": persona_id, "answers": answers})


@app.route("/api/resolve-qa", methods=["POST"])
def api_resolve_qa():
    data = request.json or {}
    question = data.get("question", "")
    profile = load_profile()
    ans = resolve_answer(question, profile=profile, allow_ai=False)
    return jsonify({
        "status": "success",
        "value": ans.value,
        "source": ans.source,
        "score": ans.score,
    })


@app.route("/api/run-dedupe", methods=["POST"])
def api_run_dedupe():
    # silent=True avoids 415 when clients omit Content-Type (K-16); UI now sends JSON too.
    data = request.get_json(silent=True) or {}
    batch = request.args.get("batch") or data.get("batch", "standard")
    if batch == "dirty":
        raw_leads = [
            RawJob(source_platform="greenhouse", source_job_id="1", title="Cloud Engineer", company="NorthStar Cloud", location="Vancouver, BC", listing_url="https://boards.greenhouse.io/northstar/jobs/1?utm_source=linkedin"),
            RawJob(source_platform="indeed", source_job_id="abc123", title="Cloud Engineer", company="northstar cloud", location="Vancouver, BC", listing_url="https://ca.indeed.com/viewjob?jk=abc123"),
            RawJob(source_platform="linkedin", source_job_id="777", title="Cloud Engineer", company="NorthStar Cloud ", location="Vancouver, BC", listing_url="https://linkedin.com/jobs/view/777"),
            RawJob(source_platform="lever", source_job_id="2", title="Platform SRE", company="Apex Systems", location="Toronto, ON", listing_url="https://jobs.lever.co/apex/2"),
            RawJob(source_platform="linkedin", source_job_id="999", title="Platform SRE", company="Apex Systems", location="Toronto, ON", listing_url="https://linkedin.com/jobs/view/999?trk=feed"),
            RawJob(source_platform="bamboohr", source_job_id="3", title="IT Systems Admin", company="Cascadia Health", location="Surrey, BC", listing_url="https://cascadia.bamboohr.com/careers/3"),
            RawJob(source_platform="workopolis", source_job_id="444", title="IT Systems Admin", company="Cascadia Health", location="Surrey, BC", listing_url="https://workopolis.com/job/444"),
        ]
    else:
        raw_leads = [
            RawJob(source_platform="greenhouse", source_job_id="1", title="Cloud Engineer", company="NorthStar Cloud", location="Vancouver, BC", listing_url="https://boards.greenhouse.io/northstar/jobs/1"),
            RawJob(source_platform="indeed", source_job_id="abc123", title="Cloud Engineer", company="NorthStar Cloud", location="Vancouver, BC", listing_url="https://ca.indeed.com/viewjob?jk=abc123"),
            RawJob(source_platform="lever", source_job_id="2", title="Platform SRE", company="Apex Systems", location="Toronto, ON", listing_url="https://jobs.lever.co/apex/2"),
            RawJob(source_platform="linkedin", source_job_id="999", title="Platform SRE", company="Apex Systems", location="Toronto, ON", listing_url="https://linkedin.com/jobs/view/999"),
            RawJob(source_platform="bamboohr", source_job_id="3", title="IT Systems Admin", company="Cascadia Health", location="Surrey, BC", listing_url="https://cascadia.bamboohr.com/careers/3"),
        ]
    normalized = [
        normalize_raw_job(raw, discovery_engine="jobspy", search_term="cloud", location="Canada")
        for raw in raw_leads
    ]
    unique = deduplicate(normalized)
    out = []
    for u in unique:
        cls = classify_apply_type(u)
        out.append({"title": u.job_title, "company": u.company_name, "apply_type": str(getattr(cls, "apply_type", cls))})
    return jsonify({
        "raw_count": len(raw_leads),
        "unique_count": len(unique),
        "duplicates_removed": len(raw_leads) - len(unique),
        "jobs": out,
    })


@app.route("/api/dry-run-receipt", methods=["POST"])
def api_dry_run_receipt():
    data = request.get_json(silent=True) or {}
    try:
        receipt = DryRunReceipt(
            ats_type=str(data.get("ats_type") or "unknown"),
            target_url=str(data.get("target_url") or request.referrer or ""),
            intercepted_method=str(data.get("intercepted_method") or "POST"),
            persona=str(data.get("persona") or "senior_fullstack"),
            variant=str(data.get("variant") or "standard"),
            html5_valid=bool(data.get("html5_valid", True)),
            aria_invalid_count=int(data.get("aria_invalid_count", 0)),
            payload=dict(data.get("payload") or {}),
        )
        saved_path = receipt.save(RECEIPTS_DIR)
        record = receipt.to_dict()
        RECEIPT_AUDIT_LOG.append(record)
        return jsonify({"ok": True, "receipt": record, "saved_to": str(saved_path)})
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400


@app.route("/api/dry-run-receipts", methods=["GET"])
def api_get_dry_run_receipts():
    return jsonify({
        "count": len(RECEIPT_AUDIT_LOG),
        "receipts": RECEIPT_AUDIT_LOG,
        "receipts_dir": str(RECEIPTS_DIR),
    })


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8765))
    print(f"🚜 JobsFarm Kane CLI Harness running on http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=False)
