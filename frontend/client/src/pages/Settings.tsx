import DashboardLayout from "@/components/layout/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  User, 
  Lock, 
  Bell, 
  Database, 
  CreditCard,
  Bot
} from "lucide-react";

export default function Settings() {
  return (
    <DashboardLayout>
      <div className="space-y-8 max-w-5xl mx-auto">
        <div>
          <h1 className="text-3xl font-bold tracking-tight mb-2">System Settings</h1>
          <p className="text-muted-foreground text-lg">
            Manage API keys, agent configurations, and user preferences.
          </p>
        </div>

        <Tabs defaultValue="general" className="space-y-6">
          <TabsList className="bg-card border border-border p-1">
            <TabsTrigger value="general" className="gap-2"><User className="w-4 h-4" /> General</TabsTrigger>
            <TabsTrigger value="agents" className="gap-2"><Bot className="w-4 h-4" /> Agents & Models</TabsTrigger>
            <TabsTrigger value="notifications" className="gap-2"><Bell className="w-4 h-4" /> Notifications</TabsTrigger>
            <TabsTrigger value="billing" className="gap-2"><CreditCard className="w-4 h-4" /> Billing</TabsTrigger>
          </TabsList>

          <TabsContent value="general" className="space-y-6">
            <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
              <CardHeader>
                <CardTitle>Profile Information</CardTitle>
                <CardDescription>Update your personal details and workspace preferences.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="name">Full Name</Label>
                    <Input id="name" defaultValue="Investment Committee" />
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="email">Email Address</Label>
                    <Input id="email" defaultValue="committee@fund.com" />
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="role">Role</Label>
                  <Input id="role" defaultValue="Senior Analyst" disabled className="bg-muted" />
                </div>
              </CardContent>
            </Card>

            <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
              <CardHeader>
                <CardTitle>Security</CardTitle>
                <CardDescription>Manage your password and 2FA settings.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between py-2">
                  <div className="space-y-0.5">
                    <Label className="text-base">Two-Factor Authentication</Label>
                    <p className="text-sm text-muted-foreground">Secure your account with 2FA.</p>
                  </div>
                  <Switch defaultChecked />
                </div>
                <div className="pt-2">
                  <Button variant="outline" className="gap-2">
                    <Lock className="w-4 h-4" /> Change Password
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="agents" className="space-y-6">
            <Card className="border-border/50 bg-card/50 backdrop-blur-sm">
              <CardHeader>
                <CardTitle>Model Configuration</CardTitle>
                <CardDescription>Select the underlying LLMs for each agent role.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid gap-6 md:grid-cols-3">
                  <div className="space-y-3 p-4 rounded-lg border border-border bg-background/50">
                    <div className="flex items-center gap-2 mb-2">
                      <div className="w-8 h-8 rounded bg-green-500/10 flex items-center justify-center text-green-500">
                        <Bot className="w-5 h-5" />
                      </div>
                      <div className="font-semibold">Sparring Partner</div>
                    </div>
                    <div className="space-y-2">
                      <Label>Provider</Label>
                      <select className="w-full h-9 rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring">
                        <option>OpenAI</option>
                        <option>Azure OpenAI</option>
                      </select>
                    </div>
                    <div className="space-y-2">
                      <Label>Model</Label>
                      <select className="w-full h-9 rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring">
                        <option>GPT-4 Turbo</option>
                        <option>GPT-4o</option>
                      </select>
                    </div>
                  </div>

                  <div className="space-y-3 p-4 rounded-lg border border-border bg-background/50">
                    <div className="flex items-center gap-2 mb-2">
                      <div className="w-8 h-8 rounded bg-purple-500/10 flex items-center justify-center text-purple-500">
                        <Bot className="w-5 h-5" />
                      </div>
                      <div className="font-semibold">Debate Analyst</div>
                    </div>
                    <div className="space-y-2">
                      <Label>Provider</Label>
                      <select className="w-full h-9 rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring">
                        <option>Anthropic</option>
                        <option>AWS Bedrock</option>
                      </select>
                    </div>
                    <div className="space-y-2">
                      <Label>Model</Label>
                      <select className="w-full h-9 rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring">
                        <option>Claude 3.5 Sonnet</option>
                        <option>Claude 3 Opus</option>
                      </select>
                    </div>
                  </div>

                  <div className="space-y-3 p-4 rounded-lg border border-border bg-background/50">
                    <div className="flex items-center gap-2 mb-2">
                      <div className="w-8 h-8 rounded bg-blue-500/10 flex items-center justify-center text-blue-500">
                        <Bot className="w-5 h-5" />
                      </div>
                      <div className="font-semibold">Deep Researcher</div>
                    </div>
                    <div className="space-y-2">
                      <Label>Provider</Label>
                      <select className="w-full h-9 rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring">
                        <option>Google Vertex AI</option>
                        <option>Google AI Studio</option>
                      </select>
                    </div>
                    <div className="space-y-2">
                      <Label>Model</Label>
                      <select className="w-full h-9 rounded-md border border-input bg-background px-3 py-1 text-sm shadow-sm transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring">
                        <option>Gemini 1.5 Pro</option>
                        <option>Gemini 1.5 Flash</option>
                      </select>
                    </div>
                  </div>
                </div>
                
                <div className="flex justify-end pt-4">
                  <Button>Save Configuration</Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  );
}
