"use client";

import { useEffect, useState } from "react";
import Shell from "@/components/layout/Shell";
import { Card, CardContent, CardHeader } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { StatusBadge } from "@/components/ui/Badge";
import { campaigns as api, contacts as contactsApi } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import { Plus, Play, Pause, Square, FileDown, Eye, Upload } from "lucide-react";

export default function CampaignsPage() {
  const [campaignList, setCampaigns] = useState<any[]>([]);
  const [view, setView] = useState<"list" | "create" | "detail">("list");
  const [selected, setSelected] = useState<any>(null);
  const [selectedContacts, setSelectedContacts] = useState<any[]>([]);

  // Create form
  const [form, setForm] = useState({ name: "", message_template: "", min_delay: 8, max_delay: 25, daily_limit: 500, scheduled_at: "" });
  const [allContacts, setAllContacts] = useState<any[]>([]);
  const [chosenIds, setChosenIds] = useState<string[]>([]);
  const [mediaFile, setMediaFile] = useState<File | null>(null);

  const loadCampaigns = () => api.list().then(setCampaigns).catch(() => {});

  useEffect(() => { loadCampaigns(); }, []);

  const openCreate = async () => {
    setView("create");
    const c = await contactsApi.list();
    setAllContacts(c);
    setChosenIds(c.map((x: any) => x.id)); // Select all by default
  };

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const campaign = await api.create({
        ...form,
        contact_ids: chosenIds,
        scheduled_at: form.scheduled_at || null,
      });
      // Upload media if any
      if (mediaFile) {
        await api.uploadMedia(campaign.id, mediaFile);
      }
      setView("list");
      loadCampaigns();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const openDetail = async (c: any) => {
    setSelected(c);
    const contacts = await api.contacts(c.id);
    setSelectedContacts(contacts);
    setView("detail");
  };

  const handleAction = async (id: string, action: "start" | "pause" | "stop") => {
    try {
      if (action === "start") await api.start(id);
      if (action === "pause") await api.pause(id);
      if (action === "stop") await api.stop(id);
      loadCampaigns();
      if (selected?.id === id) {
        const updated = await api.get(id);
        setSelected(updated);
      }
    } catch (err: any) {
      alert(err.message);
    }
  };

  const toggleContact = (id: string) => {
    setChosenIds((prev) => prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]);
  };

  return (
    <Shell>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900">Campaigns</h2>
          <div className="flex gap-2">
            {view !== "list" && <Button variant="secondary" size="sm" onClick={() => { setView("list"); loadCampaigns(); }}>← Back</Button>}
            {view === "list" && <Button size="sm" onClick={openCreate}><Plus className="w-4 h-4" /> New Campaign</Button>}
          </div>
        </div>

        {/* Campaign list */}
        {view === "list" && (
          <div className="grid gap-4">
            {campaignList.map((c) => (
              <Card key={c.id} className="hover:shadow-md transition-shadow cursor-pointer" onClick={() => openDetail(c)}>
                <CardContent className="flex items-center justify-between py-5">
                  <div>
                    <h3 className="font-semibold text-gray-900">{c.name}</h3>
                    <p className="text-sm text-gray-500 mt-1 truncate max-w-lg">{c.message_template}</p>
                    <p className="text-xs text-gray-400 mt-1">{formatDate(c.created_at)}</p>
                  </div>
                  <div className="flex items-center gap-4 text-sm">
                    <div className="text-center"><p className="text-lg font-bold text-green-600">{c.sent_count}</p><p className="text-xs text-gray-400">Sent</p></div>
                    <div className="text-center"><p className="text-lg font-bold text-red-500">{c.failed_count}</p><p className="text-xs text-gray-400">Failed</p></div>
                    <div className="text-center"><p className="text-lg font-bold text-gray-500">{c.pending_count}</p><p className="text-xs text-gray-400">Pending</p></div>
                    <StatusBadge status={c.status} />
                    <div className="flex gap-1" onClick={(e) => e.stopPropagation()}>
                      {["draft", "scheduled", "paused"].includes(c.status) && (
                        <Button variant="ghost" size="sm" onClick={() => handleAction(c.id, "start")}><Play className="w-4 h-4 text-green-600" /></Button>
                      )}
                      {c.status === "running" && (
                        <Button variant="ghost" size="sm" onClick={() => handleAction(c.id, "pause")}><Pause className="w-4 h-4 text-yellow-600" /></Button>
                      )}
                      {["running", "paused"].includes(c.status) && (
                        <Button variant="ghost" size="sm" onClick={() => handleAction(c.id, "stop")}><Square className="w-4 h-4 text-red-500" /></Button>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
            {!campaignList.length && (
              <Card><CardContent className="py-12 text-center text-gray-400">No campaigns yet. Create your first one!</CardContent></Card>
            )}
          </div>
        )}

        {/* Create */}
        {view === "create" && (
          <Card>
            <CardHeader><h3 className="font-semibold">Create Campaign</h3></CardHeader>
            <CardContent>
              <form onSubmit={handleCreate} className="space-y-5 max-w-2xl">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Campaign Name</label>
                  <Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} placeholder="March Promotion" required />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Message Template</label>
                  <textarea
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-brand-500 min-h-[120px]"
                    value={form.message_template}
                    onChange={(e) => setForm({ ...form, message_template: e.target.value })}
                    placeholder={"Hello {Name}, we have a special offer for you! 🎉\n\nVisit our store for 20% off all items this weekend."}
                    required
                  />
                  <p className="text-xs text-gray-400 mt-1">Use <code>{"{Name}"}</code> to personalize with contact name</p>
                </div>
                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Min Delay (sec)</label>
                    <Input type="number" value={form.min_delay} onChange={(e) => setForm({ ...form, min_delay: +e.target.value })} min={3} />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Max Delay (sec)</label>
                    <Input type="number" value={form.max_delay} onChange={(e) => setForm({ ...form, max_delay: +e.target.value })} min={5} />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Daily Limit</label>
                    <Input type="number" value={form.daily_limit} onChange={(e) => setForm({ ...form, daily_limit: +e.target.value })} min={1} />
                  </div>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Schedule (optional)</label>
                  <Input type="datetime-local" value={form.scheduled_at} onChange={(e) => setForm({ ...form, scheduled_at: e.target.value })} />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Attach Media (optional)</label>
                  <input type="file" onChange={(e) => setMediaFile(e.target.files?.[0] || null)} className="text-sm" />
                </div>

                {/* Contact selection */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <label className="text-sm font-medium text-gray-700">Select Contacts ({chosenIds.length} / {allContacts.length})</label>
                    <div className="flex gap-2">
                      <Button type="button" variant="ghost" size="sm" onClick={() => setChosenIds(allContacts.map((c: any) => c.id))}>Select All</Button>
                      <Button type="button" variant="ghost" size="sm" onClick={() => setChosenIds([])}>Deselect All</Button>
                    </div>
                  </div>
                  <div className="max-h-48 overflow-auto border rounded-lg p-2 space-y-1">
                    {allContacts.map((c: any) => (
                      <label key={c.id} className="flex items-center gap-2 px-2 py-1 hover:bg-gray-50 rounded cursor-pointer text-sm">
                        <input type="checkbox" checked={chosenIds.includes(c.id)} onChange={() => toggleContact(c.id)} className="rounded" />
                        <span className="font-medium">{c.name}</span>
                        <span className="text-gray-400">{c.phone}</span>
                      </label>
                    ))}
                    {!allContacts.length && <p className="text-gray-400 text-center py-4">No contacts. Import some first.</p>}
                  </div>
                </div>

                <Button type="submit" size="lg" disabled={!chosenIds.length}>Create Campaign</Button>
              </form>
            </CardContent>
          </Card>
        )}

        {/* Detail */}
        {view === "detail" && selected && (
          <div className="space-y-4">
            <Card>
              <CardContent className="py-5">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="text-xl font-bold">{selected.name}</h3>
                    <p className="text-sm text-gray-500 mt-1 whitespace-pre-wrap">{selected.message_template}</p>
                    <p className="text-xs text-gray-400 mt-2">Created {formatDate(selected.created_at)} • Delay {selected.min_delay}–{selected.max_delay}s • Limit {selected.daily_limit}/day</p>
                  </div>
                  <div className="flex items-center gap-3">
                    <StatusBadge status={selected.status} />
                    <a href={`/api/campaigns/${selected.id}/report`} className="inline-flex items-center gap-1 text-sm text-brand-600 hover:underline"><FileDown className="w-4 h-4" /> Report</a>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader><h4 className="font-semibold">Contacts ({selectedContacts.length})</h4></CardHeader>
              <CardContent>
                <div className="overflow-auto max-h-[500px]">
                  <table className="w-full text-sm">
                    <thead className="sticky top-0 bg-white"><tr className="border-b text-left text-gray-500">
                      <th className="pb-2">Name</th><th className="pb-2">Phone</th><th className="pb-2">Status</th><th className="pb-2">Sent At</th><th className="pb-2">Error</th>
                    </tr></thead>
                    <tbody>
                      {selectedContacts.map((c) => (
                        <tr key={c.id} className="border-b border-gray-50">
                          <td className="py-2">{c.name}</td>
                          <td className="py-2 text-gray-600">{c.phone}</td>
                          <td className="py-2"><StatusBadge status={c.status} /></td>
                          <td className="py-2 text-gray-400 text-xs">{formatDate(c.sent_at)}</td>
                          <td className="py-2 text-red-400 text-xs truncate max-w-xs">{c.error_message}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </Shell>
  );
}
