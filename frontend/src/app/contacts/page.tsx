"use client";

import { useEffect, useState, useRef } from "react";
import { useSearchParams } from "next/navigation";
import Shell from "@/components/layout/Shell";
import { Card, CardContent, CardHeader } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import { Badge, StatusBadge } from "@/components/ui/Badge";
import { contacts as contactsApi } from "@/lib/api";
import { formatDate } from "@/lib/utils";
import { Upload, Plus, Trash2, Download, Search, CheckCircle, XCircle } from "lucide-react";

export default function ContactsPage() {
  const params = useSearchParams();
  const [tab, setTab] = useState<"list" | "upload" | "add">(params.get("tab") === "upload" ? "upload" : "list");
  const [contactList, setContacts] = useState<any[]>([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(false);

  // Upload state
  const [preview, setPreview] = useState<any[] | null>(null);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadResult, setUploadResult] = useState<any>(null);
  const fileRef = useRef<HTMLInputElement>(null);

  // Add form
  const [form, setForm] = useState({ name: "", phone: "", group_name: "" });

  const loadContacts = () => {
    contactsApi.list(search ? `search=${search}` : "").then(setContacts).catch(() => {});
  };

  useEffect(() => { loadContacts(); }, [search]);

  // Upload preview
  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploadFile(file);
    setUploadResult(null);
    setLoading(true);
    try {
      const rows = await contactsApi.uploadPreview(file);
      setPreview(rows);
    } catch (err: any) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = async () => {
    if (!uploadFile) return;
    setLoading(true);
    try {
      const res = await contactsApi.uploadConfirm(uploadFile);
      setUploadResult(res);
      setPreview(null);
      loadContacts();
    } catch (err: any) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAdd = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await contactsApi.create(form);
      setForm({ name: "", phone: "", group_name: "" });
      setTab("list");
      loadContacts();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm("Delete this contact?")) return;
    await contactsApi.delete(id);
    loadContacts();
  };

  return (
    <Shell>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900">Contacts</h2>
          <div className="flex gap-2">
            <Button variant={tab === "list" ? "primary" : "secondary"} size="sm" onClick={() => setTab("list")}>All Contacts</Button>
            <Button variant={tab === "upload" ? "primary" : "secondary"} size="sm" onClick={() => setTab("upload")}><Upload className="w-4 h-4" /> Upload Excel</Button>
            <Button variant={tab === "add" ? "primary" : "secondary"} size="sm" onClick={() => setTab("add")}><Plus className="w-4 h-4" /> Add</Button>
            <a href="/api/contacts/export" className="inline-flex items-center gap-2 px-3 py-1.5 text-xs font-medium border border-gray-300 rounded-lg hover:bg-gray-50">
              <Download className="w-4 h-4" /> Export
            </a>
          </div>
        </div>

        {/* List */}
        {tab === "list" && (
          <Card>
            <CardHeader>
              <div className="relative w-80">
                <Search className="absolute left-3 top-2.5 w-4 h-4 text-gray-400" />
                <Input className="pl-9" placeholder="Search name or phone…" value={search} onChange={(e) => setSearch(e.target.value)} />
              </div>
            </CardHeader>
            <CardContent>
              <table className="w-full text-sm">
                <thead><tr className="border-b text-left text-gray-500">
                  <th className="pb-2">Name</th><th className="pb-2">Phone</th><th className="pb-2">Group</th><th className="pb-2">Tags</th><th className="pb-2">Created</th><th className="pb-2"></th>
                </tr></thead>
                <tbody>
                  {contactList.map((c) => (
                    <tr key={c.id} className="border-b border-gray-50 hover:bg-gray-50">
                      <td className="py-2.5 font-medium">{c.name}</td>
                      <td className="py-2.5 text-gray-600">{c.phone}</td>
                      <td className="py-2.5">{c.group_name && <Badge color="blue">{c.group_name}</Badge>}</td>
                      <td className="py-2.5 flex gap-1 flex-wrap">{c.tags?.map((t: any) => <Badge key={t.id}>{t.name}</Badge>)}</td>
                      <td className="py-2.5 text-gray-400 text-xs">{formatDate(c.created_at)}</td>
                      <td className="py-2.5"><button onClick={() => handleDelete(c.id)} className="text-red-400 hover:text-red-600"><Trash2 className="w-4 h-4" /></button></td>
                    </tr>
                  ))}
                  {!contactList.length && <tr><td colSpan={6} className="py-8 text-center text-gray-400">No contacts yet</td></tr>}
                </tbody>
              </table>
            </CardContent>
          </Card>
        )}

        {/* Upload */}
        {tab === "upload" && (
          <Card>
            <CardHeader><h3 className="font-semibold">Upload Excel File</h3></CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-gray-500">Upload an <code>.xlsx</code> file with columns: <strong>Name</strong>, <strong>PhoneNumber</strong>, <strong>Message</strong> (optional)</p>
              <div className="flex items-center gap-4">
                <input ref={fileRef} type="file" accept=".xlsx" onChange={handleFileChange} className="hidden" />
                <Button variant="secondary" onClick={() => fileRef.current?.click()} disabled={loading}>
                  <Upload className="w-4 h-4" /> {loading ? "Processing…" : "Choose File"}
                </Button>
                {uploadFile && <span className="text-sm text-gray-600">{uploadFile.name}</span>}
              </div>

              {/* Preview table */}
              {preview && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium">
                      Preview: {preview.filter((r) => r.valid).length} valid / {preview.filter((r) => !r.valid).length} invalid of {preview.length} rows
                    </p>
                    <Button onClick={handleConfirm} disabled={loading || !preview.some((r) => r.valid)}>
                      <CheckCircle className="w-4 h-4" /> Import Valid Contacts
                    </Button>
                  </div>
                  <div className="max-h-96 overflow-auto border rounded-lg">
                    <table className="w-full text-sm">
                      <thead className="bg-gray-50 sticky top-0"><tr>
                        <th className="px-3 py-2 text-left">Row</th><th className="px-3 py-2 text-left">Name</th>
                        <th className="px-3 py-2 text-left">Phone</th><th className="px-3 py-2 text-left">Message</th>
                        <th className="px-3 py-2 text-left">Status</th>
                      </tr></thead>
                      <tbody>
                        {preview.map((r, i) => (
                          <tr key={i} className={r.valid ? "" : "bg-red-50"}>
                            <td className="px-3 py-1.5">{r.row}</td>
                            <td className="px-3 py-1.5">{r.name}</td>
                            <td className="px-3 py-1.5">{r.phone}</td>
                            <td className="px-3 py-1.5 text-gray-500 truncate max-w-xs">{r.message}</td>
                            <td className="px-3 py-1.5">
                              {r.valid
                                ? <span className="text-green-600 flex items-center gap-1"><CheckCircle className="w-3.5 h-3.5" /> Valid</span>
                                : <span className="text-red-500 flex items-center gap-1"><XCircle className="w-3.5 h-3.5" /> {r.error}</span>}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {uploadResult && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-sm">
                  ✅ Imported <strong>{uploadResult.created}</strong> contacts. Skipped <strong>{uploadResult.skipped_duplicates}</strong> duplicates. <strong>{uploadResult.errors}</strong> errors.
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Add form */}
        {tab === "add" && (
          <Card>
            <CardHeader><h3 className="font-semibold">Add Contact</h3></CardHeader>
            <CardContent>
              <form onSubmit={handleAdd} className="space-y-4 max-w-md">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                  <Input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Phone (with country code)</label>
                  <Input value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} placeholder="+1234567890" required />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Group (optional)</label>
                  <Input value={form.group_name} onChange={(e) => setForm({ ...form, group_name: e.target.value })} placeholder="VIP Customers" />
                </div>
                <Button type="submit">Add Contact</Button>
              </form>
            </CardContent>
          </Card>
        )}
      </div>
    </Shell>
  );
}
